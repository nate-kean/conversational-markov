import random
from typing import Literal, cast

import markovify


BEGIN = markovify.text.BEGIN
RESPONSE = "__RESPONSE__"
WILDCARD = "__WILDCARD__"
type WildcardState = tuple[str | Literal["__WILDCARD__"], ...]

PUNCTUATION = r"""!"#$%&'()*+,-./;=?@[\]^_`{|}~"""


class ConvMark:
	def __init__(self, parsed_sentences: list[list[str]]):
		"""
		parsed_sentences element format:
		word, word, RESPONSE, word, ...
		"""
		self.markov = markovify.Text(
			None,
			parsed_sentences=parsed_sentences,
			state_size=3,
		)
		self.markov.compile(inplace=True)

	def respond(self, input_message: str) -> str:
		init_state = self.make_init_state(input_message)
		result = self.markov.make_sentence(
			init_state=init_state,
			test_output=False,
		)
		if result is None:
			return "Error"
		preamble_length = 0
		for token in init_state:
			preamble_length += len(token) + 1
		return result[preamble_length:]

	def resolve_wildcards(
		self,
		wild_state: WildcardState,
	) -> markovify.chain.State | None:
		"""
		Choose a state that is like the given state in all the part that aren't
		wildcards.
		"""
		states = self.markov.chain.model.keys()
		# Filter the haystack of states down to just the ones that match all the
		# needle state's non-wild parts.
		for i, part in enumerate(wild_state):
			if part == WILDCARD:
				continue
			# Filter the haystack of states down to just the ones that match
			# this non-wild part of the wild state.
			states = [state for state in states if state[i] == part]
		if len(states) == 0:
			return None
		return random.choice(cast(list[markovify.chain.State], states))

	def make_init_state(self, input_message: str) -> markovify.chain.State:
		"""
		Settle for a state that is less-and-less similar from the one that comes
		from the input message, based on what is available in the model.
		"""
		first, last = encode_prompt(input_message)
		# Best case: the model knows this state exactly
		state = (first, last, RESPONSE)
		if state in self.markov.chain.model:
			return state
		# Next best: model knows a state with just the first word
		state = self.resolve_wildcards((first, WILDCARD, RESPONSE))
		if state is not None:
			return state
		# Next best: just the last word
		state = self.resolve_wildcards((WILDCARD, last, RESPONSE))
		if state is not None:
			return state
		# Try permutations
		state = self.resolve_wildcards((last, first, RESPONSE))
		if state is not None:
			return state
		state = self.resolve_wildcards((WILDCARD, first, RESPONSE))
		if state is not None:
			return state
		state = self.resolve_wildcards((last, WILDCARD, RESPONSE))
		if state is not None:
			return state
		# Worst case: no matches. Just go random
		state = self.resolve_wildcards((WILDCARD, WILDCARD, RESPONSE))
		assert state is not None, (
			"Corrupt: corpus does not contain the RESPONSE token"
		)
		return state


def encode_word(word: str) -> str:
	if word[0] in PUNCTUATION:
		word = word[1:]
	if len(word) == 0:
		return WILDCARD
	if word[-1] in PUNCTUATION:
		word = word[:-1]
	if len(word) == 0:
		return WILDCARD
	return word.lower()


def encode_prompt(text: str) -> tuple[str, str]:
	words = text.split()
	first = encode_word(words[0]) if len(words) >= 1 else WILDCARD
	last = encode_word(words[-1]) if len(words) >= 2 else WILDCARD
	return first, last

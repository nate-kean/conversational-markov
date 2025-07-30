# Conversational Markov

LLMs don't normally sound like they're talking to you. The LLM in its most 
basic state simply continues the text it's given. LLMs sound like they're
talking to you when they're set up to complete _one_ side of a conversation.

Technically, there's nothing stopping you from making a Markov chain that does
this, too. Train it on runs that have a prompt and a response, delineated by
a sentinel token, and then, during inference, you can make the starting state
any given prompt followed by the sentinel, and it will autocomplete something
that sounds like a fitting response.

This project explores that.  
Now, practically, there are reasons Markov chains are _not_ typically used this
way: state size would increase linearly with every extra word you want to be
able to prompt with, and model size will correspondingly increase exponentially.
With just a handful of prompt words and a decent sized corpus, you'll be running
out of memory trying to load the whole thing.  
But still, I wanted to try it, because LLM inference takes a lot of compute,
meanwhile Markov chain generators don't. What I can get away with on a €5 Hetzner
box?

This project is a naïve example of a framework around a Markov chain which sets
it up to respond to prompts. It uses a state size of 3, enough to allow it to
process just the first and last word of a prompt plus the sentinel token.
When you prompt it with something it's seen before, it really does make more
coherent-seeming responses than a conventional Markov chain does from a random
state.

Avenues for improvement:
- Decouple token length of prompt from state size of response generation. I.e.,
  allow a longer starting state to increase number of tokens that can be included
  in the prompt without also having to increase the state size used to generate
  the response. State size of 3 is already pretty large for making remotely
  original sounding responses, but at the same time, it's really small for
  ingesting a prompt. A Dynamic State Size Markov Chain?

# Question brief: Reinforcement Learning (`mod-rl`)

Subject: Deep Learning, GenAI, MLOps, System Design
Topics: 6

For each topic below, write at least 4 self-check questions in
`content/questions/mod-rl.yaml`. Ground every question in the PRIMARY
resource listed for that topic: the learner will have just read that page, and the
question exists to check they took the right thing from it.

---

## `rl-mdp-fundamentals` — MDP fundamentals

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Define the reinforcement learning problem in MDP terms and read the notation used in RL papers.
- Context: States, actions, trajectories, reward, return and the RL optimisation problem stated formally, with a diagram-led second pass for the notation.
- Resources:
  - **PRIMARY** OpenAI — Part 1: Key Concepts in RL
    https://spinningup.openai.com/en/latest/spinningup/rl_intro.html
  - **REFERENCE** Hugging Face — Introduction to Deep Reinforcement Learning
    https://huggingface.co/learn/deep-rl-course/unit1/introduction
    exact part: Sections "The RL Framework" and "The reward hypothesis"
- Currently has **no questions at all**.

## `rl-policy-vs-value` — Policies and value functions

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Explain how a value function is defined recursively and what separates a policy from a value estimate.
- Context: The Bellman recursion, and the four value functions (V, Q, V*, Q*) that it makes computable.
- Resources:
  - **PRIMARY** Hugging Face — The Bellman Equation: simplify our value estimation
    https://huggingface.co/learn/deep-rl-course/unit2/bellman-equation
  - **REFERENCE** OpenAI — Part 1: Key Concepts in RL
    https://spinningup.openai.com/en/latest/spinningup/rl_intro.html
    exact part: Sections "Value Functions" and "Bellman Equations"
- Currently has **no questions at all**.

## `rl-q-learning` — Q-learning

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Implement tabular Q-learning and explain why it is off-policy.
- Context: The tabular Q-learning update rule with a worked example, epsilon-greedy exploration, and the off-policy convergence claim behind it.
- Resources:
  - **PRIMARY** Hugging Face — Introducing Q-Learning
    https://huggingface.co/learn/deep-rl-course/unit2/q-learning
  - **REFERENCE** incompleteideas.net (Sutton & Barto) — Reinforcement Learning: An Introduction (2nd ed.)
    http://incompleteideas.net/book/RLbook2020.pdf
    exact part: §6.5 "Q-learning: Off-policy TD Control" (pp. 131–132)
- Currently has **no questions at all**.

## `rl-policy-gradients` — Policy gradients

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Derive the policy gradient and state the loss a REINFORCE implementation actually minimises.
- Context: Deriving the policy gradient from scratch down to the loss you would code, including reward-to-go and baselines, plus where policy optimisation sits in the RL algorithm taxonomy.
- Resources:
  - **PRIMARY** OpenAI — Part 3: Intro to Policy Optimization
    https://spinningup.openai.com/en/latest/spinningup/rl_intro3.html
  - **REFERENCE** OpenAI — Part 2: Kinds of RL Algorithms
    https://spinningup.openai.com/en/latest/spinningup/rl_intro2.html
- Currently has **no questions at all**.

## `rl-rlhf-mechanics` — RLHF mechanics

- Depth target: STRONG  ·  Track: SPECIALIZATION
- Objective: Explain the RLHF pipeline stage by stage, including what the KL penalty is protecting.
- Context: The three-stage RLHF pipeline: pretrained model, reward model trained on preferences, then PPO with a KL penalty against the reference model.
- Resources:
  - **PRIMARY** Hugging Face — Illustrating Reinforcement Learning from Human Feedback (RLHF)
    https://huggingface.co/blog/rlhf
- Currently has **no questions at all**.

## `rl-bandits-for-ranking` — Contextual bandits for ranking

- Depth target: WORKING_KNOWLEDGE  ·  Track: SPECIALIZATION
- Objective: Frame a recommendation problem as a contextual bandit and say how you would evaluate a policy offline.
- Context: Where RL actually shows up in product work: contextual bandits for recommendation, explore/exploit policies, regret, and the offline-evaluation problem.
- Resources:
  - **PRIMARY** VowpalWabbit — Contextual Bandits
    https://vowpalwabbit.org/docs/vowpal_wabbit/python/latest/tutorials/python_Contextual_bandits_and_Vowpal_Wabbit.html
  - **REFERENCE** arXiv — A Contextual-Bandit Approach to Personalized News Article Recommendation
    https://arxiv.org/abs/1003.0146
    exact part: Abstract, §1 Introduction, §3 (LinUCB)
- Currently has **no questions at all**.


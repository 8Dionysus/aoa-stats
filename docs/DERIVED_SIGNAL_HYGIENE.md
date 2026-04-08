# Derived Signal Hygiene

## Purpose

Wave 4 introduces more derived signals into the same neighborhood:

- eval reports
- recovery-window summaries
- route hints
- memo pattern objects

That can get slippery fast.
This guide keeps the layer clean.

## Primary Rule

Derived surfaces may reinforce each other, but they must not build a closed loop that outranks owner evidence.

A healthy precedence chain is:

1. source-owned receipts and owner-local artifacts
2. bounded eval reports
3. derived stats summaries
4. derived route hints
5. memo recall objects

Any builder or consumer that flips that order is drifting.

## Safe Use Of Route Hints

Route hints can help choose the next read or next bounded inspection path.
They should not be treated as direct evidence that recovery succeeded.

## Safe Use Of Memo Pattern Objects

Memo pattern objects can remind the system that a repeated recovery pattern exists.
They should not be treated as proof that the present run fits the pattern.

## Safe Use Of Summaries

A window summary can say that recovery posture looked healthier across a named window.
It should not declare a surface ready for mutation by itself.

## Wave 4 Note

The easiest mistake here is a glittering loop where proof, stats, routing, and memo all cite each other and forget the owner receipt.
Do not build that mirror maze.

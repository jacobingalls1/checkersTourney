This is a somewhat unorthodox attempt at a checkers engine (work is ongoing)

An important concept with this engine is extremely lean memory usage.
Board states and moves are encoded in bitwise representations of an 8x8 checkerboard.
This means that decision trees can be stored between runs with less space and with much less load time.
Specifically, this yields around 10x space save compared to a somewhat naive OOP approach with the same decision strategy.
Because of a somewhat novel method of calculating and representing moves with bitshifts and masks, there is also a significant speed up to search depth, but this has not been well explored and memory was the focus.
The eventual goal for this compression is to use limited machine learning to adapt to opponents mid-match or even mid-game. 
Specifically, to prune the search tree based not only on the valuation of board states, but also on the evaluation of the opponent's psychology.


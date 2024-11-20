#!/usr/bin/env python3

import sys
import argparse
import random

def make_goal(size: int) -> list:
    total_size = size * size
    puzzle = [-1] * total_size
    current = 1
    x = 0
    ix = 1
    y = 0
    iy = 0
    
    while True:
        puzzle[x + y * size] = current
        if current == 0:
            break
        current += 1
        
        if (x + ix == size or x + ix < 0 or 
            (ix != 0 and puzzle[x + ix + y * size] != -1)):
            iy = ix
            ix = 0
        elif (y + iy == size or y + iy < 0 or 
              (iy != 0 and puzzle[x + (y + iy) * size] != -1)):
            ix = -iy
            iy = 0
        
        x += ix
        y += iy
        if current == size * size:
            current = 0
    
    return puzzle

def make_puzzle(size: int, solvable: bool, iterations: int) -> list:
    def swap_empty(p: list) -> None:
        idx = p.index(0)
        possible_moves = []
        
        if idx % size > 0:
            possible_moves.append(idx - 1)
        if idx % size < size - 1:
            possible_moves.append(idx + 1)
        if idx // size > 0:
            possible_moves.append(idx - size)
        if idx // size < size - 1:
            possible_moves.append(idx + size)
            
        swap_idx = random.choice(possible_moves)
        p[idx], p[swap_idx] = p[swap_idx], p[idx]
    
    puzzle = make_goal(size)
    for _ in range(iterations):
        swap_empty(puzzle)
    
    if not solvable:
        if puzzle[0] == 0 or puzzle[1] == 0:
            puzzle[-1], puzzle[-2] = puzzle[-2], puzzle[-1]
        else:
            puzzle[0], puzzle[1] = puzzle[1], puzzle[0]
    
    return puzzle

def main():
    parser = argparse.ArgumentParser(description="Generate N-puzzle instances")
    
    parser.add_argument("size", type=int, 
                       help="Size of the puzzle's side. Must be ≥3.")
    parser.add_argument("-s", "--solvable", action="store_true", 
                       help="Forces generation of a solvable puzzle. Overrides -u.")
    parser.add_argument("-u", "--unsolvable", action="store_true",
                       help="Forces generation of an unsolvable puzzle")
    parser.add_argument("-i", "--iterations", type=int, default=10000,
                       help="Number of random moves to make")
    
    args = parser.parse_args()
    
    if args.solvable and args.unsolvable:
        print("Can't be both solvable AND unsolvable!")
        sys.exit(1)
    
    if args.size < 3:
        print("Can't generate a puzzle with size lower than 3.")
        sys.exit(1)
    
    if not args.solvable and not args.unsolvable:
        solvable = random.choice([True, False])
    else:
        solvable = args.solvable
    
    puzzle = make_puzzle(args.size, solvable, args.iterations)
    
    width = len(str(args.size * args.size))
    with open("puzzle.txt", "w") as f:
        f.write(f"# This puzzle is {'solvable' if solvable else 'unsolvable'}\n")
        f.write(f"{args.size}\n")
        for y in range(args.size):
            row = []
            for x in range(args.size):
                num = puzzle[x + y * args.size]
                row.append(str(num).rjust(width))
            f.write(" ".join(row) + "\n")

if __name__ == "__main__":
    main()
import random

def generate_npuzzle(size: int, filename: str):
   """
   Generates a random N-puzzle and writes it to a file.
   First line is size, then the puzzle grid.
   """
   numbers = [x for x in range(0, size * size)]
   random.shuffle(numbers)
   
   with open(filename, 'w') as f:
       f.write(f"{size}\n")
       
       for i in range(0, size * size, size):
           row = numbers[i:i + size]
           f.write(" ".join(str(x) for x in row) + "\n")

generate_npuzzle(3, "test_puzzle.txt")

print("Generated puzzle:")
with open("test_puzzle.txt", 'r') as f:
   print(f.read())
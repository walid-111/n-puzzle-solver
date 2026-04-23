NAME = npuzzle

all: $(NAME)

$(NAME):
	@echo "Nothing to compile, Python is interpreted"

run:
	python3 npuzzle-solver.py puzzles/3-solvable.txt

fclean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

re: fclean all

.PHONY: all run fclean re
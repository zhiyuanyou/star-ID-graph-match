export PYTHONPATH=./:$PYTHONPATH

python -u ./tools/search.py --std_position $1 --num_lost $2 --num_false $3

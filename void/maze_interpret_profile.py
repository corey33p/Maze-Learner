import pstats

with open('out.txt', 'w') as stream:
    stats = pstats.Stats('void\stats.txt', stream=stream)
    stats.print_stats()

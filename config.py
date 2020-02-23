platform = "nano"

# general params
MAX_THREADS = 4
MIN_ULTRALONG_LEN = 10000

# filenames
ALIGNMENTS_FILENAME = "alignment.bed"
CHAINS_FILENAME = "alignment.txt"
ALLKMERS_FILENAME = "all_kmers.txt"
KMERS_FILENAME = "kmers.txt"
SOLID_KMERS_FILENAME = "solid_kmers.txt"
GOODKMERS_FILENAME = "one_clump_kmers.txt"
SAM_FILENAME = "alignment.sam"
NUCL_ALIGN_DIRNAME = "nucl_align"

# k-mer params
KMER_SIZE = 19
KMER_SELECT_WINDOW_SIZE = 10000
MIN_OCCURRENCES = 5
MAX_OCCURRENCES = 1000
MIN_FREQ = 0.0
MAX_FREQ = 1
MAX_KMER_FREQ = 100

# mapping params
MIN_CHAIN_LEN = 3000
MIN_CHAIN_KMERS = 10
MAX_REF_GAP = 5000
MAX_MISSED_KMERS = 500

# plot params
NUM_XTICKS = 8

# bp params
MIN_BP_COV = 10
MIN_TIP_LEN = 5000
BP_WINDOW_SIZE = 1000
MOVING_AVG_WINDOW_SIZE = 200

# kmer analysis
MIN_CLUMP_SIZE = 2
MAX_CLUMP_DIST = 1000
KMER_WINDOW_SIZE = 20000

# monomer and unit analysis
MIN_COV = 5
TMER_SIZE = 3
MONOMER_GAP_SIZE = 500
MONOMER_AVG_SIZE = 170
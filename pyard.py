import pyard

ard=pyard.init()
print(ard)

print(f"Allele\tG\tP\tlg\tlgx\tW\texon\tU2\tS\t")




allele = "B*15:01P"
print(f"{allele}\t{ard.redux(allele, 'G')}\t{ard.redux(allele, 'P')}\t{ard.redux(allele, 'lg')} \
	{ard.redux(allele, 'lgx')}\t{ard.redux(allele, 'W')}\t{ard.redux(allele, 'exon')} \
	{ard.redux(allele, 'U2')}\t{ard.redux(allele, 'S')}\t")


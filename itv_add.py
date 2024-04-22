source_file = open("itv0.txt", "r")
target_file = open("itv.txt", "a")

content = source_file.read()
target_file.write(content)

source_file.close()
target_file.close()

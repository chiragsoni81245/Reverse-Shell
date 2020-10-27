with open("t.txt","w") as f:
    for i in range(500000):
        f.write("{} Hello Chirag\n".format(i+1))

with open("t.txt","rb") as f:
    data = f.read()
    print("Lenght: {}".format(len(data)))
    print("Chunk Size: {}".format( len(data)//20 ))
def takeFirst(elem):
    return elem[0]
def takeSecond(elem):
    return elem[1]
def takeThird(elem):
    return elem[2]

def getSolutionString(counts):
    return takeFirst(max(counts, key=takeSecond))

def parseSolution(sol):
    return [int(i) for i in sol]

def figureToBase64(fig):
    import matplotlib.pyplot as plt
    import io
    import base64
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='png', bbox_inches='tight')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode("utf-8")
    plt.savefig('temp_visualized.png',format='png', bbox_inches='tight')
    plt.close(fig)
    return my_base64_jpgData
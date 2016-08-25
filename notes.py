import re
scrubbed = []

for i in range(len(ss)):
    a = re.sub(r'\([^)]*\)','',ss[i])
    scrubbed.append(a)
s = []
for i in range(len(ss)):
     a = re.sub('\s?\(.+\)\s?','',ss[i])
     b = re.sub('\s?\[.+\]\s?','',a)
     c = re.sub('\s?official lyric video\s?','',b,flags=re.IGNORECASE)
     d = re.split('\s?-\s?',c)
     s.append(d) 

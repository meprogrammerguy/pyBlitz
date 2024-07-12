    if c == 5:
        left_text = s[index:].partition(":")
        s_valid = s[index:].partition("OFF")
        print ("left_text[0]: " + left_text[0])
        print ("OFF: s_valid[0]: " + s_valid[0])
        pdb.set_trace()
    left_text = s[index:].partition(":")
    s_valid = s[index:].partition("OFF")
    if left_text[1]:
        #print ("found :")
        #print (str(left_text[0]))
        #pdb.set_trace()
            fields.append(left_text[0][:-2])
            index+=len(left_text[0][:-2])
        #pdb.set_trace()
    else:
        #print ("no :")
        #pdb.set_trace()
        if s_valid[1] and (len(s_valid[0]) <= len(left_text[0])):
            pdb.set_trace()
        #o_idx=3
        #idx_f = FirstUpper(s_valid[2])
        #print ("found OFF: idx_f: " + str(idx_f))
        #o_idx+=(idx_f)
        #print ("found OFF: o_idx: " + str(o_idx))
            fields.append(s_valid[0] + s_valid[1])
            index+=(len(s_valid[0]) + len(s_valid[1]))
            pdb.set_trace()
        else:
            fields.append(s[index:])
            index+=len(s[index:])

    #o_idx=0
    #if s_valid[1] and (len(s_valid[0]) <= len(left_text[0])):
        #pdb.set_trace()
        #o_idx=3
        #idx_f = FirstUpper(s_valid[2])
        #print ("found OFF: idx_f: " + str(idx_f))
        #o_idx+=(idx_f)
        #print ("found OFF: o_idx: " + str(o_idx))
        #fields.append(s_valid[0] + s_valid[1])
        #index+=(len(s_valid[0]) + len(s_valid[1]))
        #pdb.set_trace()
    #else:
        
    #fields.append(s[index:index+idx_f+o_idx])
    #index+=(idx_f+o_idx)

        #if left_text[1]:
        #print ("found :")
        #print (str(left_text[0]))
        #pdb.set_trace()
            #fields.append(left_text[0][:-2])
            #index+=len(left_text[0][:-2])
        #pdb.set_trace()
        #else:
        #print ("no :")
        #pdb.set_trace()
            #fields.append(s[index:])
            #index+=len(s[index:])
    print ("field 13: " + fields[12])
    print (" index end: " + str(index))

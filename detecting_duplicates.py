from imutils import paths
import numpy as np
import argparse
import cv2
import os


apo = argparse.ArgumentParser()

apo.add_argument('-i','--imagepath',required = True, help = 'Path to the directory where images are stored')
apo.add_argument('-s','--size',required = True, type = int, help = 'Size of the image for hashing')
apo.add_argument('-r','--remove',default = "no", help = 'Type yes if you wish to remove the duplicate images')
args = vars(apo.parse_args())


def diff_hash(img, size):
    #taking only the grayscale image

    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dim = (size+1, size) #(width, height)
    re_img = cv2.resize(img, dim)
    #we now need to calculate if the left pixel is brighter than the right pixel
    diff_bool = re_img[:,:size] > re_img[:,1:]
    flat = diff_bool.flatten()
    
    return (sum([2 ** i for (i, v) in enumerate(flat) if v]))

#loop over all the images to make a dictionary with hash as key and the images that share that key as value
#images with common hashes are the duplicates we want to handle

pathlist = list(paths.list_images(args["imagepath"]))
#a dictionary with key of hash and values of images which share that hash
hashdict = {}

for i in pathlist:
    img = cv2.imread(i)
    hashval = diff_hash(img, args["size"])
    #checing if that hash to stored previously
    #this will return a list of paths with same hash
    #if not, it will be empty. 
    #Add the path to that hash value
    paths = hashdict.get(hashval,[])
    paths.append(i)
    
    #update this list of images with the corresponding hash value
    hashdict[hashval] = paths

#viewing the duplicate images
dupl = 0
common_hash = 0
for (hashv, imgpath) in hashdict.items():
    if len(imgpath) > 1:
        dupl = dupl + len(imgpath)
        common_hash = common_hash + 1
        if args["remove"] == "no":
        
            montage = None
            
            #loop over the images in the imgpath
            for i in imgpath:
                img = cv2.imread(i)
                img = cv2.resize(img, (150,150))
                
                if montage is None:
                    montage = img
                else: 
                    #stacking the montage and img column wise
                    montage = np.hstack([montage, img])
                    
            print("[INFORMATION] hash: {}".format(hashv))
            cv2.imshow("Montage hash: {}".format(hashv), montage)
            cv2.waitKey(0)
            
        else:
            #if wish to remove
            #all the images with more than one copy will be removed
            #except for the first one
            for x in imgpath[1:]:
                os.remove(x)
            print("[INFORMATION] Deleting duplicate images")
print("-------------\n         ")
print("[INFORMATION] Total number of common hash values found: {}".format(common_hash))              
print("[INFORMATION] Total number of duplicates found: {}".format(dupl))
difference  = dupl - common_hash
print("[INFORMATION] Total number of extra images : {}".format(difference))


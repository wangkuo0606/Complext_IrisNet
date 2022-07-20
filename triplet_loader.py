from PIL import Image
import os
import os.path
import torch.utils.data
import torchvision.transforms as transforms
import random

def default_image_loader(path):
    return Image.open(path).convert('L')

class TripletImageLoader(torch.utils.data.Dataset):
    def __init__(self, base_path, mask_path, transform=None, loader=default_image_loader):
        self.base_path = base_path  
        self.mask_path = mask_path
        self.subjects = sorted(os.listdir(base_path))
        self.samples = dict()
        for sbj in self.subjects:
            self.samples[sbj+'/L'] = os.listdir(os.path.join(base_path, sbj+'/L'))
        self.triplets = []
        for sbj in self.subjects:
            for i, anchor in enumerate(self.samples[sbj]):
                for positive in self.samples[sbj][i+1:]:
                    if positive == None:
                        continue
                    while True:
                        negSbj = random.choice(self.subjects)
                        if negSbj != sbj:
                            break
                    negative = random.choice(self.samples[negSbj])
                    self.triplets.append((os.path.join(base_path, sbj, anchor),
                                    os.path.join(base_path, sbj, positive),
                                    os.path.join(base_path, negSbj, negative),
                                    os.path.join(mask_path, sbj, anchor),
                                    os.path.join(mask_path, sbj, positive),
                                    os.path.join(mask_path, negSbj, negative),
                                    ))
        self.transform = transform
        self.transform2 = transforms.Compose([transforms.ToTensor(), transforms.Resize((8, 32))])
        self.loader = loader

    def __getitem__(self, index):
        a, p, n, ma, mp, mn = self.triplets[index]
        imgA = self.loader(a)
        imgP = self.loader(p)
        imgN = self.loader(n)
        maskA = self.transform2(self.loader(ma)).bool()
        maskP = self.transform2(self.loader(mp)).bool()
        maskN = self.transform2(self.loader(mn)).bool()
        if self.transform is not None:
            imgA = self.transform(imgA)
            imgP = self.transform(imgP)
            imgN = self.transform(imgN)
        
        return imgA, imgP, imgN, maskA, maskP, maskN

    def __len__(self):
        return len(self.triplets)


def default_image_loader(path):
    return Image.open(path).convert('L')


class TestImageLoader(torch.utils.data.Dataset):
    def __init__(self, base_path, mask_path, transform=None, loader=default_image_loader):
        self.base_path = base_path
        self.mask_path = mask_path
        self.subjects = sorted(os.listdir(base_path))
        self.samples = list()
        self.masks = list()
        self.labels =list()
  
        for sbj in self.subjects:
            samples = sorted(os.listdir(os.path.join(base_path, sbj)))
            for sample in samples:
                self.samples.append(os.path.join(base_path, sbj, sample))
                self.masks.append(os.path.join(mask_path, sbj, sample))
                self.labels.append(sbj)           
        if transform is None:
            self.transform = transforms.Compose([transforms.ToTensor()])
        else:
            self.transform = transform
        self.transform2 = transforms.Compose(
            [transforms.ToTensor(), transforms.Resize((8, 32))])
        self.loader = loader

    def __getitem__(self, index):
        img = self.transform(self.loader(self.samples[index]))   
        mask = self.transform2(self.loader(self.masks[index])).bool()
        label = self.labels[index]

        return img, mask, label

    def __len__(self):
        return len(self.samples)

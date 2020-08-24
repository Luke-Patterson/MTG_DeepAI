from torch.utils.data import Dataset

class NumbersDataset(Dataset):
    def __init__(self):
        self.samples = list(range(1, 1001))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


if __name__ == '__main__':
    dataset = NumbersDataset()
    print(len(dataset))
    print(dataset[100])
    print(dataset[122:361])
    

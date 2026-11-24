from pipeline import load_nflverse, load_kaggle, load_pfr

if __name__ == "__main__":
    print("nflverse")
    load_nflverse.run()
    print("Kaggle BDB")
    load_kaggle.run()
    print("PFR")
    load_pfr.run()
    print("Done")

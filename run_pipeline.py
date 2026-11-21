from pipeline import load_nflverse, load_kaggle, load_pfr

if __name__ == "__main__":
    print("=== nflverse ===")
    load_nflverse.run()

    print("\n=== Kaggle (Big Data Bowl) ===")
    load_kaggle.run()

    print("\n=== PFR ===")
    load_pfr.run()

    print("\nPipeline complete.")

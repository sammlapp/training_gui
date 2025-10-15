import numpy as np
import pandas as pd
import os


def check_clip_df_format(df):
    assert df.index.names == (
        "file",
        "start_time",
        "end_time",
    ), f"expected the first 3 columns of the csv to be `file,start_time,end_time` but got {df.index.names}"


def process_fully_annotated_files(config, logger=None):
    """Load and process fully annotated files"""
    fully_annotated_dfs = []

    for f in config.get("fully_annotated_files", []):
        if logger:
            logger.info(f"Loading fully annotated file: {f}")
        df = pd.read_csv(f, index_col=[0, 1, 2])
        check_clip_df_format(df)

        # columns are either one per class with one-hot labels, or "labels" and "complete"
        if "labels" in df.columns:
            # parse labels column (list of strings) to list
            import ast

            df["labels"] = df["labels"].apply(ast.literal_eval)
            df = df[df.complete == "complete"]

            # use opensoundscape utility for labels to one-hot
            from opensoundscape.annotations import categorical_to_multi_hot

            multihot_labels = pd.DataFrame(
                categorical_to_multi_hot(
                    df["labels"].values, classes=config["class_list"], sparse=False
                ),
                index=df.index,
                columns=config["class_list"],
            )
        else:
            # df should have one-hot labels: just select the correct classes
            multihot_labels = df[config["class_list"]]

        fully_annotated_dfs.append(multihot_labels)

    if fully_annotated_dfs:
        return pd.concat(fully_annotated_dfs)[config["class_list"]]
    else:
        return pd.DataFrame(columns=config["class_list"])


def process_single_class_annotations(config, labels, logger=None):
    """Adds single-class annotations to set of fully annotated labels"""
    # add labels where only one species was annotated
    # treat other species as weak negatives, storing NaN as label

    single_class_dfs = []

    for annotation_item in config.get("single_class_annotations", []):
        file_path = annotation_item["file"]
        class_name = annotation_item["class"]
        if logger:
            logger.info(
                f"Loading single class annotation file: {file_path} for class: {class_name}"
            )
        df = pd.read_csv(file_path, index_col=[0, 1, 2])
        check_clip_df_format(df)

        # remove incomplete or uncertain annotations
        df = df[df.annotation.isin(["yes", "no"])]

        # create one-hot df
        # treat any other classes as weak negatives, using NaN value
        new_labels = pd.DataFrame(np.nan, index=df.index, columns=config["class_list"])
        new_labels[class_name] = df["annotation"].map({"yes": 1, "no": 0})
        single_class_dfs.append(new_labels)

    if not single_class_dfs:
        return labels  # nothing to add

    # combine single-class labels across species
    # if same clip is annotated for mutiple species,
    # combine the labels (ie 1&NaN=1, 0&NaN=0, NaN&NaN=NaN)
    single_labels = pd.concat(single_class_dfs)
    single_labels = single_labels.groupby(single_labels.index).max()

    # Combine with fully annotated labels
    if not labels.empty:
        # if any samples are in both fully annotated and single class, prefer fully annotated
        single_labels = single_labels[~single_labels.index.isin(labels.index)]
        labels = pd.concat([labels, single_labels])
    else:
        labels = single_labels

    return labels


def load_background_samples(config, max_background_samples=10_000, logger=None):
    """Load background samples if provided

    This would typically be environmental noise with none of the classes present

    Samples are used for overlay (aka mixup) in which the sample is blended with a training sample

    # TODO: allow selecting a folder of audio or list of files instead of providing df?
    """
    background_samples_file = config.get("background_samples_file", "")
    if background_samples_file and os.path.exists(background_samples_file):
        if logger:
            logger.info(f"Loading background samples from: {background_samples_file}")
        background_samples = pd.read_csv(background_samples_file, index_col=[0, 1, 2])
        check_clip_df_format(background_samples)

        # subset to a maximum of 10,000, which should be plenty of variety
        if len(background_samples) > max_background_samples:
            background_samples = background_samples.sample(n=max_background_samples)

        return background_samples
    return None


def load_evaluation_data(config, logger=None):
    """Load evaluation data if provided"""
    evaluation_file = config.get("evaluation_file", "")
    if evaluation_file and os.path.exists(evaluation_file):
        if logger:
            logger.info(f"Loading evaluation data from: {evaluation_file}")
        return pd.read_csv(evaluation_file, index_col=[0, 1, 2])
    return None

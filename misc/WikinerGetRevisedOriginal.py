from pathlib import Path

from loaders.WikinerGoldLoader import WikinerGoldLoader 
from loaders.WikinerLoader import WikinerLoader 
import tqdm


def GetPrerevisedWikinerDocuments():
    full_path = r"D:\Informatyka\Magisterka\code\datasets\wikiner\5462500\aij-wikiner-fr-wp2"
    dataset = WikinerLoader.LoadDatasetSentencesLocal(full_path)

    full_path = r"D:\Informatyka\Magisterka\code\datasets\wikiner-fr-gold\wikiner-fr-gold.conll"
    dataset2 = WikinerGoldLoader.LoadDatasetLocal(full_path)

    ogs = []
    not_found = []
    doc_txt = {document.plain_text: document for document in dataset.documents}

    for doc2 in tqdm.tqdm(dataset2.documents):
        document = doc_txt.get(doc2.plain_text,None)
        if document != None:
            ogs.append(document)
        else:
            not_found.append(doc2)
        # if doc.plain_text in doc2_txt:
        #     ogs.append(doc)

    raw_text = "\n\n".join( [doc.raw_text for doc in ogs])

    write_path = Path(r"D:\Informatyka\Magisterka\code\datasets\wikiner-fr-pre-gold")
    write_path.mkdir(exist_ok=True)
    write_path = write_path / "wikiner-fr.conll"
    with open(write_path, encoding="utf-8", mode="+w") as file:
        file.write(raw_text)

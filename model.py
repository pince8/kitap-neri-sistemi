import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from difflib import get_close_matches

# 📌 Veri Yükleme ve Temizleme
df = pd.read_csv("Books_df.csv")

df["text"] = df["Title"].astype(str) + " " + df["Main Genre"].astype(str)

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\d+', '', text)
    return text.strip()

df["clean_text"] = df["text"].apply(clean_text)

# 📌 TF-IDF Vektörleme
vectorizer = TfidfVectorizer(max_features=500)
X_tfidf = vectorizer.fit_transform(df["clean_text"]).toarray()

# 📌 K-Means Kümeleme Modeli
kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(X_tfidf)

# 📌 Kitap Önerme Fonksiyonu
from difflib import get_close_matches

def recommend_books(book_title, top_n=5):
    """
    Belirtilen kitap başlığına benzer kitapları önerir.
    Küçük/büyük harf farkı ve kısmi metin aramasını destekler.
    Eşleşme bulunamazsa 'Kitap bulunamadı' mesajını döndürür.
    """
    title_list = df["Title"].str.lower().tolist()  # Tüm başlıkları küçük harfe çeviriyoruz

    # 1. Kısmi metin ve case‐insensitive eşleşmeyi dene
    mask = df["Title"].str.lower().str.contains(book_title.lower(), na=False)  # Kullanıcı girdiği metni küçük harfe çeviriyor
    if mask.any():
        idx = df[mask].index[0]
    else:
        # 2. Yakın başlıkları difflib ile dene, ancak cutoff değerini artırıyoruz (0.6 gibi)
        matches = get_close_matches(book_title.lower(), title_list, n=1, cutoff=0.6)  # Burada da kullanıcının metnini küçük harfe çeviriyoruz
        if not matches:
            return "Kitap bulunamadı"  # hiç eşleşme yok, kitap bulunamadı mesajı döndürüyoruz
        idx = df[df["Title"].str.lower() == matches[0]].index[0]  # Başlıklar küçük harfe çevrilmişken eşleşme yapıyoruz

    # Kitap başlığını bulduk ve aynı küme içindeki kitapları öneriyoruz
    cluster = df.loc[idx, "Cluster"]
    similar = df[df["Cluster"] == cluster].index.tolist()
    similar.remove(idx)  # Kendini önerme
    if not similar:
        return "Kitap bulunamadı"  # Benzer kitap yoksa kitap bulunamadı mesajı döndürüyoruz

    # 📌 Kosinüs benzerliği hesaplama
    book_vec = X_tfidf[idx].reshape(1, -1)
    sims = cosine_similarity(book_vec, X_tfidf[similar])[0]
    
    # 📌 Benzerlik sıralama
    best = np.argsort(sims)[::-1][:top_n]
    recs = df.iloc[[similar[i] for i in best]][["Title", "Main Genre", "Rating"]]
    
    return recs.to_dict(orient="records")
    try:
        book_idx = df[df["Title"] == book_title].index[0]
        cluster = df.loc[book_idx, "Cluster"]

        similar_books = df[df["Cluster"] == cluster].index.tolist()
        if book_idx in similar_books:
            similar_books.remove(book_idx)  # Kendini önerme

        if not similar_books:
            print("Benzer kitap bulunamadı!")
            return []

        # 📌 Kosinüs benzerliği hesaplama
        book_vector = X_tfidf[book_idx].reshape(1, -1)
        similarities = cosine_similarity(book_vector, X_tfidf[similar_books])
        
        # 📌 Benzerlik sıralama
        sorted_indices = np.argsort(similarities[0])[::-1][:top_n]
        recommended_books = df.iloc[[similar_books[i] for i in sorted_indices]][["Title", "Main Genre", "Rating"]]
        
        return recommended_books.to_dict(orient="records")
    
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return []

import pandas as pd

# CSV dosyasını oku
df = pd.read_csv('Books_df.csv')

# Tür sütununu kontrol et
genre_column = 'Main Genre' if 'Main Genre' in df.columns else 'Genre'

# Boş olmayanlardan 100 farklı türde kitap seç
books = df.dropna(subset=[genre_column]).drop_duplicates(subset=[genre_column]).head(100)

# Seçilecek alanlar: Başlık, Yazar, Tür, Puan
selected_books = books[['Title', 'Author', genre_column, 'Rating']].reset_index(drop=True)
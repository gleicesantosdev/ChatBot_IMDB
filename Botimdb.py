import customtkinter as ctk
import pandas as pd
import unicodedata
import re
import gdown
import os

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("IMDb Assistant")
        master.geometry("800x600")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=700, height=400, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou seu assistente IMDb. Você pode fazer perguntas como:\n\n" +
                            "1. Buscar por título: 'Mostre informações sobre [título]'\n" +
                            "2. Buscar por diretor: 'Quais séries são dirigidas por [diretor]?'\n" +
                            "3. Buscar por ano: 'Quais títulos foram lançados em [ano]?'\n" +
                            "4. Buscar por gênero: 'Mostre títulos do gênero [gênero]'\n" +
                            "5. Estatísticas: 'Mostrar estatísticas gerais'\n\n")
        self.text_area.configure(state="disabled")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=600, placeholder_text="Digite sua pergunta...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

        # Carregar dados
        self.load_data()

    def load_data(self):
        try:
            file_path = 'data.csv' 
            if not os.path.exists(file_path):
                print("Baixando dataset...")
                url = 'https://drive.google.com/uc?id=1gZ7lWHLO8d2GYJfK4V3OOHcuAjjK3I3P'  
                gdown.download(url, file_path, quiet=False)
            
            self.data = pd.read_csv(file_path)
        except Exception as e:
            self.data = None
            print(f"Erro ao carregar dados: {e}")

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "\nVocê: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        response = self.get_response(user_input)

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Assistente: " + response + "\n")
        self.text_area.see("end")
        self.text_area.configure(state="disabled")

        self.entry.delete(0, ctk.END)

    def normalize_string(self, s):
        if isinstance(s, str):
            return unicodedata.normalize('NFKD', s.lower()).encode('ASCII', 'ignore').decode('utf-8')
        return str(s).lower()

    def get_response(self, user_input):
        if self.data is None:
            return "Desculpe, não foi possível carregar a base de dados."

        user_input_lower = self.normalize_string(user_input)

        # Busca por título
        if "mostre informações sobre" in user_input_lower:
            title = user_input_lower.replace("mostre informações sobre", "").strip()
            return self.search_by_title(title)

        # Busca por diretor
        elif "dirigidos por" in user_input_lower:
            director = user_input_lower.split("dirigidos por")[1].strip()
            return self.search_by_director(director)

                # Busca por ano
        elif "lançados em" in user_input_lower:
            try:
                year = int(re.search(r'\d{4}', user_input_lower).group())
                return self.search_by_year(year)
            except:
                return "Por favor, especifique um ano válido (ex: 2020)"

        # Busca por gênero
        elif "gênero" in user_input_lower:
            genre = user_input_lower.split("gênero")[1].strip()
            return self.search_by_genre(genre)

        # Estatísticas gerais
        elif "estatísticas" in user_input_lower:
            return self.get_statistics()

        else:
            return "Desculpe, não entendi sua pergunta. Por favor, tente uma das opções sugeridas."

    def search_by_title(self, title):
        matches = self.data[self.data['Series_Title'].apply(self.normalize_string).str.contains(title, na=False)]
        if matches.empty:
            return "Nenhum título encontrado."
        
        result = matches.iloc[0]
        return f"Título: {result['Series_Title']}\n" + \
               f"Tipo: {result['Type']}\n" + \
               f"Diretor: {result['Director']}\n" + \
               f"Ano: {result['Year']}\n" + \
               f"Gêneros: {result['Genre']}\n" + \
               f"Descrição: {result['Description']}"

    def search_by_director(self, director):
        matches = self.data[self.data['Director'].apply(self.normalize_string).str.contains(director, na=False)]
        if matches.empty:
            return "Nenhum diretor encontrado."
        
        titles = matches['Series_Title'].tolist()
        return f"Títulos dirigidos por {director}:\n" + "\n".join(f"- {title}" for title in titles[:5])

    def search_by_year(self, year):
        matches = self.data[self.data['Year'] == year]
        if matches.empty:
            return f"Nenhum título encontrado para o ano {year}."
        
        titles = matches['Series_Title'].tolist()
        return f"Títulos lançados em {year}:\n" + "\n".join(f"- {title}" for title in titles[:5])

    def search_by_genre(self, genre):
        matches = self.data[self.data['Genre'].apply(self.normalize_string).str.contains(genre, na=False)]
        if matches.empty:
            return f"Nenhum título encontrado no gênero {genre}."
        
        titles = matches['Series_Title'].tolist()
        return f"Títulos do gênero {genre}:\n" + "\n".join(f"- {title}" for title in titles[:5])

    def get_statistics(self):
        total_titles = len(self.data)
        series = len(self.data[self.data['Type'] == 'TV Show'])
        
        top_directors = self.data['Director'].value_counts().head(5)
        top_genres = self.data['Genre'].str.split(', ', expand=True).stack().value_counts().head(5)
        
        stats = f"Estatísticas gerais:\n\n" \
                f"Total de títulos: {total_titles}\n" \
                f"Séries de TV: {series}\n\n" \
                f"Top 5 diretores:\n"
        
        for director, count in top_directors.items():
            stats += f"- {director}: {count} títulos\n"
        
        stats += f"\nTop 5 gêneros:\n"
        for genre, count in top_genres.items():
            stats += f"- {genre}: {count} títulos\n"
        
        return stats

def main():
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()

if __name__ == "__main__":
    main()
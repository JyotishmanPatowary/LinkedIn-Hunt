import tkinter as tk 
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

class LinkedInJobScraper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("LinkedIn Job Scraper")
        self.window.geometry("800x600")
        
        # Style configuration
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=4)
        
        self.create_gui()
        
    def create_gui(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.window, text="Search Parameters", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Job Title
        ttk.Label(input_frame, text="Job Title:").grid(row=0, column=0, sticky="w")
        self.job_title = ttk.Entry(input_frame, width=30)
        self.job_title.grid(row=0, column=1, padx=5, pady=5)
        
        # Location
        ttk.Label(input_frame, text="Location:").grid(row=1, column=0, sticky="w")
        self.location = ttk.Entry(input_frame, width=30)
        self.location.grid(row=1, column=1, padx=5, pady=5)
        
        # Number of pages to scrape
        ttk.Label(input_frame, text="Pages to scrape:").grid(row=2, column=0, sticky="w")
        self.pages = ttk.Entry(input_frame, width=10)
        self.pages.insert(0, "1")
        self.pages.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Scrape Button
        self.scrape_button = ttk.Button(input_frame, text="Start Scraping", command=self.start_scraping)
        self.scrape_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Filepath Entry
        ttk.Label(input_frame, text="Save Location:").grid(row=4, column=0, sticky="w")
        self.filepath = ttk.Entry(input_frame, width=30)
        self.filepath.grid(row=4, column=1, padx=5, pady=5)

        # Browse Button
        self.browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=4, column=2, padx=5, pady=5)

        # Results Frame
        results_frame = ttk.LabelFrame(self.window, text="Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Results Text Area
        self.results_area = scrolledtext.ScrolledText(results_frame, width=70, height=20)
        self.results_area.pack(fill="both", expand=True)
        
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.filepath.delete(0, tk.END)
            self.filepath.insert(0, folder_selected)
    
    def construct_url(self, page=0):
        base_url = "https://www.linkedin.com/jobs/search"
        keywords = self.job_title.get().replace(" ", "%20")
        location = self.location.get().replace(" ", "%20")
        return f"{base_url}?keywords={keywords}&location={location}&start={page*25}"
    
    def scrape_jobs(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            jobs_list = []
            job_cards = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')
            
            for card in job_cards:
                try:
                    title = card.find('h3', class_='base-search-card__title').text.strip()
                    company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                    location = card.find('span', class_='job-search-card__location').text.strip()
                    job_link = card.find('a', class_='base-card__full-link')['href']
                    
                    jobs_list.append({
                        'Title': title,
                        'Company': company,
                        'Location': location,
                        'URL': job_link
                    })
                except AttributeError:
                    continue
                    
            return jobs_list
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return []
    
    def start_scraping(self):
        self.results_area.delete(1.0, tk.END)
        self.results_area.insert(tk.END, "Starting job search...\n\n")
        
        try:
            pages_to_scrape = int(self.pages.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of pages")
            return
        
        all_jobs = []
        
        for page in range(pages_to_scrape):
            url = self.construct_url(page)
            jobs = self.scrape_jobs(url)
            all_jobs.extend(jobs)
            
            self.results_area.insert(tk.END, f"Scraped page {page + 1}...\n")
            self.window.update()
            
            # Respect rate limits
            time.sleep(random.uniform(2, 4))
        
        # Save results
        if all_jobs:
            save_location = self.filepath.get()
            if not save_location:
                messagebox.showerror("Error", "Please select a folder to save the file.")
                return
                
            filename = f"{save_location}/linkedin_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df = pd.DataFrame(all_jobs)
            df.to_csv(filename, index=False)
            
            self.results_area.insert(tk.END, f"\nFound {len(all_jobs)} jobs!\n")
            self.results_area.insert(tk.END, f"Results saved to {filename}\n\n")
            
            # Display preview of results
            self.results_area.insert(tk.END, "Preview of found jobs:\n")
            for i, job in enumerate(all_jobs[:10], 1):
                self.results_area.insert(tk.END, f"\n{i}. {job['Title']}\n")
                self.results_area.insert(tk.END, f"   Company: {job['Company']}\n")
                self.results_area.insert(tk.END, f"   Location: {job['Location']}\n")
        else:
            self.results_area.insert(tk.END, "No jobs found. Try different search parameters.\n")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = LinkedInJobScraper()
    app.run()

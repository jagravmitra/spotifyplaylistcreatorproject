import tkinter as tk #importing tkinter for GUI
from tkinter import messagebox, simpledialog, ttk #import tkinter compements for dialog boxes
from spotipy import Spotify #import spotify client
from spotipy.oauth2 import SpotifyOAuth #import spotify ouath for authentication
import webbrowser #import webbrowser to play track previews

CLIENT_ID = "spotifyclientid" #spotify client id
CLIENT_SECRET = "spotifyclientsecret"
REDIRECT_URI =  "http://localhost:8888/callback" # redirect uri for spotify oauth

#creating main app class
class SpotifyPlaylistCreator:
    def __init__(self, root):
        # Initialize Spotify API authentication
        self.sp = Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,  # Set client ID
            client_secret=CLIENT_SECRET,  # Set client secret
            redirect_uri=REDIRECT_URI,  # Set redirect URI
            scope="playlist-modify-public playlist-modify-private"  # Specify required scopes
        ))

        # Main window setup
        self.root = root  # Reference to the main window
        self.root.title("Spotify Playlist Creator")  # Set the window title
        self.root.geometry("600x700")  # Set the window dimensions
        self.current_theme = "dark"  # Set the default theme to dark

        # Create a canvas for scrollable content
        self.canvas = tk.Canvas(root, bg="black")  # Create a canvas with a black background
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)  # Add a vertical scrollbar
        self.scrollable_frame = tk.Frame(self.canvas, bg="black")  # Create a frame inside the canvas

        # Configure the canvas to adjust its scroll region dynamically
        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Embed the frame into the canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)  # Connect the scrollbar to the canvas

        # Pack the canvas and scrollbar into the main window
        self.canvas.pack(side="left", fill="both", expand=True)  # Fill the left side with the canvas
        self.scrollbar.pack(side="right", fill="y")  # Fill the right side with the scrollbar

        # Add title label
        title = tk.Label(self.scrollable_frame, text="Spotify Playlist Creator",font=("Arial", 18, "bold"), bg="black", fg="green")  # Title label
        title.pack(pady=10)  # Add padding around the title


        # Add mood selection section
        tk.Label(self.scrollable_frame, text="Select Moods", bg="black", fg="green", font=("Arial", 12)).pack(pady=5)  # Label for moods section
        self.mood_frame = tk.Frame(self.scrollable_frame, bg="black")  # Frame for mood checkboxes
        self.mood_frame.pack(pady=10)  # Add padding around the mood frame

        # List of available moods
        self.moods = ["Happy", "Sad", "Energetic", "Relaxing", "Romantic", "Focus", "Angry", "Cheerful", "Calm"]
        self.mood_vars = {mood: tk.BooleanVar() for mood in self.moods}  # Create a variable for each mood

        # Add checkboxes for each mood
        for mood in self.moods:
            tk.Checkbutton(self.mood_frame, text=mood, variable=self.mood_vars[mood], bg="black", fg="green", selectcolor="black").pack(anchor="w")  # Create mood checkbox

        # Add genre selection section
        tk.Label(self.scrollable_frame, text="Select Genres:", bg="black", fg="green", font=("Arial", 12)).pack(pady=5)  # Label for genres section
        self.genre_frame = tk.Frame(self.scrollable_frame, bg="black")  # Frame for genre checkboxes
        self.genre_frame.pack(pady=10)  # Add padding around the genre frame

        # List of available genres
        self.genres = ["Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "Electronic", "R&B", "Country"]
        self.genre_vars = {genre: tk.BooleanVar() for genre in self.genres}  # Create a variable for each genre

        # Add checkboxes for each genre
        for genre in self.genres:
            tk.Checkbutton(self.genre_frame, text=genre, variable=self.genre_vars[genre], bg="black", fg="green", selectcolor="black").pack(anchor="w")  # Create genre checkbox

        # Add customization options section
        tk.Label(self.scrollable_frame, text="Customization Options", bg="black", fg="green", font=("Arial", 12)).pack(pady=5)  # Label for customization options
        tk.Label(self.scrollable_frame, text="Number of Tracks", bg="black", fg="green").pack()  # Label for track count
        self.track_count = tk.Scale(self.scrollable_frame, from_=10, to=50, orient="horizontal", bg="black", fg="green", highlightbackground="black")  # Slider for track count
        self.track_count.pack(pady=5)  # Add padding around the slider

        # Add privacy option
        self.privacy_var = tk.BooleanVar()  # Variable for privacy setting
        tk.Checkbutton(self.scrollable_frame, text="Make Playlist Private", variable=self.privacy_var, bg="black", fg="green", selectcolor="black").pack(pady=5)  # Checkbox for privacy option

        # Add preview button
        preview_button = tk.Button(self.scrollable_frame, text="Preview Tracks", command=self.preview_tracks, bg="green", fg="black")  # Button to preview tracks
        preview_button.pack(pady=10)  # Add padding around the preview button

        # Add create playlist button
        create_button = tk.Button(self.scrollable_frame, text="Create Playlist", command=self.create_playlist, bg="green", fg="black")  # Button to create playlist
        create_button.pack(pady=10)  # Add padding around the create button


    def get_selected_moods_and_genres(self):
        #getting the selected moods and genres
        selected_moods = [mood for mood, var in self.mood_vars.items() if var.get()] #getting the list of selected moods
        selected_genres = [genre for genre, var in self.genre_vars.items() if var.get()] #list of selected genres
        return selected_moods, selected_genres

    def preview_tracks(self):
        #showing preview of the tracks
        selected_moods, selected_genres = self.get_selected_moods_and_genres() #getting the user selected moods and genres
        if not selected_moods and not selected_genres: #checking if mood or genres are selected
            messagebox.showerror("Error", "Please select a mood or genre.") #error message
            return

        #contructing the search query
        query = " ".join(selected_moods + selected_genres) # combine the mood and genre
        results = self.sp.search(q = query, type = "track", limit = self.track_count.get()) #search the tracks


        #open new window for preview
        preview_window = tk.Toplevel(self.root) #create a new top-level
        preview_window.title("Track Preview") #title of the window
        preview_window.geometry("400x600") #setting window size

        for idx, track in enumerate(results["trakcs"]["items"]): #iterate through search results
            track_name = track["name"] #get track name
            track_artists = track["artists"][0]["name"] #getting the track artist
            preview_url = track["preview_url"] #getting track preview url
            tk.Label(preview_window, text = "{idx + 1}. {track_name} by {track_artist}", wraplength = 380).pack(pady = 2)  # showing track details
            if preview_url: #check is the preview url is available
                tk.Button(preview_window, text = "Play Preview", command = lambda url = preview_url: webbrowser.open(url)).pack() #play the preview button


    def create_playlist(self):
        selected_moods, selected_genres = self.get_selected_moods_and_genres() #getting the user selected moods and genres
        if not selected_moods and not selected_genres: #checking if mood or genres are selected
            messagebox.showerror("Error", "Please select a mood or genre.") #error message
            return

        #contructing the search query
        query = " ".join(selected_moods + selected_genres) # combine the mood and genre
        results = self.sp.search(q = query, type = "track", limit = self.track_count.get()) #search the tracks
        track_uris = [track["uri"] for track in results["tracks"]["items"]] #get tracks uris

        #asking the user for playlist name
        playlist_name = simpledialog.askstring("Playlist Name", "Enter the name for your playlist: ")
        if not playlist_name: #check is the user cancelled
            return

        #creating the playlist 
        playlist = self.sp.user_playlist_create(
            user = self.sp.me()['id'], #get the current user id
            name = playlist_name, #set playlist name
            public = not self.privacy_var.get() ##set privacy based on user input
        )
        self.sp.playlist_add_items(playlist_id = ["id"], items = track_uris) #add tracks to the playlist
        messagebox.showinfo("Succes", "Playlist {playlist_name} created succesfully") #show success message

#run the application
if __name__ == "__main__":
    root = tk.Tk() # create the main window
    app = SpotifyPlaylistCreator(root) #creating the app instance
    root.mainloop()

















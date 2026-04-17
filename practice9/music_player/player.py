import os
import pygame


class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()

        self.music_folder = music_folder
        self.playlist = self.load_tracks()
        self.current_index = 0

        self.is_playing = False
        self.is_paused = False
        self.current_track_start_time = 0

        if not self.playlist:
            raise ValueError("No music files found in the music folder.")

    def load_tracks(self):
        tracks = []
        for file_name in os.listdir(self.music_folder):
            if file_name.endswith(".mp3") or file_name.endswith(".wav"):
                tracks.append(file_name)

        tracks.sort()
        return tracks

    def get_current_track_path(self):
        return os.path.join(self.music_folder, self.playlist[self.current_index])

    def get_current_track_name(self):
        return self.playlist[self.current_index]

    def play(self):
        track_path = self.get_current_track_path()
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_paused = False
        self.current_track_start_time = pygame.time.get_ticks()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def next_track(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_status(self):
        if self.is_playing:
            return "Playing"
        return "Stopped"

    def get_progress_seconds(self):
        if self.is_playing:
            current_time = pygame.time.get_ticks()
            return (current_time - self.current_track_start_time) // 1000
        return 0
    

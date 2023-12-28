import os
import music21 as m21
import json
import tensorflow
from tensorflow import keras
import numpy as np

us = m21.environment.UserSettings()
us['musescoreDirectPNGPath']  = 'C:/Program Files/MuseScore 4/bin/MuseScore4.exe'
us['musicxmlPath'] = 'C:/Program Files/MuseScore 4/bin/MuseScore4.exe'
# File where Musescore 4 is: 'C:/Program Files/MuseScore 4/bin/MuseScore4.exe'
# The above does not really work but I can make txt document then use song.write to make it a XML file.
# Then I can go to MuseScore4 and run the XML file in the XML_Files folder. Write for loop to go through list and make XML file
# for each song.


# In[2]:


KERN_DATASET_PATH = "deutschl/erk"
SAVE_DIR = "dataset"
SINGLE_FILE_DATASET = "file_dataset"
SEQUENCE_LENGTH = 64
MAPPING_PATH = "C:/Users/reese/Documents/JuceTest/JuceTest/Source/mapping.json"

# 1 is a quarter note, 0.25 is sixteenth note, 4 is whole note
ACCEPTABLE_DURATIONS = [
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2,
    3,
    4
]

def load_songs_in_kern(dataset_path):
    
    songs = []
    
    #go through all the files in dataset and load them with music21
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            if file[-3:] == "krn":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs

# want to make things easier no crazy note lengths
def has_acceptable_durations(song, acceptable_durations):
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

def transpose(song):
    
    # get the key from the song if annotated, key stored at beginning of first part
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    #where the key is stored usually in the dataset
    key = measures_part0[0][4]   
    
    # estimate key using music21 if not annotated
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")
        
    print(key)
    # get the interval for transposition, how far away we need to transpose
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
        
    # transpose song by the interval
    transposed_song = song.transpose(interval)
    
    return transposed_song

def encode_song(song, time_step=0.25):
    # p=60, d=1 -> [60, -.-.-]  (midi note pitch and duration using 16th notes, a quarter note is 4 16th notes)
    #time step is 16th note
    
    encoded_song = []
    
    for event in song.flat.notesAndRests:
        
        # handle notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi #60
        
        # handle rests
        elif isinstance(event, m21.note.Rest):
            symbol = "r"
            
        #convert note or rest to time series
        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
                
    #cast encoded song to string
    encoded_song = " ".join(map(str, encoded_song))
    
    return encoded_song

def preprocess(dataset_path):
    pass

    #load the folk songs
    print("Loading songs...")
    songs=load_songs_in_kern(dataset_path)
    print(f"Loaded {len(songs)} songs.")
    
    for i, song in enumerate(songs): 
        
        #filter out songs that have non acceptable durations
        if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
            continue
        
        #transpose songs to Cmaj / Amin
        song = transpose(song)
        
        #encode songs with music time series representations
        encoded_song = encode_song(song)

        #save songs to text file, w is write mode
        save_path = os.path.join(SAVE_DIR, str(i))
        with open(save_path, "w") as fp:
            fp.write(encoded_song)
            
def load(file_path):
    with open(file_path, "r") as fp:
        song = fp.read()
    return song
            

def create_single_file_dataset(dataset_path, file_dataset_path, sequence_length):
    
    new_song_delimiter = "/ " * sequence_length 
    songs = ""
    
    #load encoded songs and add delimiters
    for path, _, files in os.walk(dataset_path):
        for file in files:
            file_path = os.path.join(path, file)
            song = load(file_path)
            songs = songs + song + " " + new_song_delimiter
            
    songs = songs[:-1]
    
    #save string that contains all dataset
    with open(file_dataset_path, "w") as fp:
        fp.write(songs)
        
    return songs

def create_mapping(songs, mapping_path):
    mappings = {}
    
    #identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))
    
    #create a mapping
    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i
    
    # save vocab to json file
    with open(mapping_path, "w") as fp:
        json.dump(mappings, fp, indent = 4)
        
def convert_songs_to_int(songs):
    int_songs=[]
    
    # load mappings for dict
    with open(MAPPING_PATH, "r") as fp:
        mappings = json.load(fp)
    
    # cast songs string to a list
    songs = songs.split()
    
    # map songs to int
    for symbol in songs:
        int_songs.append(mappings[symbol])
        
    return int_songs

def generate_training_sequences(sequence_length):
    # [11,12,13,14,...] -> i: [11,12], t: 13; i: [12,13], t: 14
    
    # load songs and map to int
    songs = load(SINGLE_FILE_DATASET)
    int_songs = convert_songs_to_int(songs)
    
    # generate the training sequences
    # 100 symbols, 64 sl, 100-64 = 36
    inputs = []
    targets = []
    
    num_sequences = len(int_songs) - sequence_length
    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])
    
    # one hot encode sequences
    vocabulary_size = len(set(int_songs))
    inputs = keras.utils.to_categorical(inputs, num_classes=vocabulary_size)
    targets = np.array(targets)
    
    return inputs, targets
        
def main():
    preprocess(KERN_DATASET_PATH)
    songs = create_single_file_dataset(SAVE_DIR, SINGLE_FILE_DATASET, SEQUENCE_LENGTH)
    create_mapping(songs, MAPPING_PATH)
    inputs, targets = generate_training_sequences(SEQUENCE_LENGTH)

    
if __name__ == "__main__":
    main()

    #songs = load_songs_in_kern(KERN_DATASET_PATH)
    #print(f"Loaded {len(songs)} songs.")
    #song = songs[0]    
    #transposed_song = transpose(song)
    #song.write('musicxml','XML_Files/XML_test.xml')
    #print("The first XML file is stored in XML_test.xml.")
    #transposed_song.write('musicxml','XML_Files/XML_test2.xml')
    #print("The second XML file is stored in XML_test2.xml.")
    
    
# TODO: look up music21 documentation(code my own songs), kern format, do test codes on terms above i dont know
# list of terms: m21.converter.parse, song.flat.notesAndRests, song, note.duration.quarterLength
# music plugin ideas: generate a melody in C major or A minor, choose major or minor 
# music plugin ideas: input your own melodies and have it give a melody 


# In[ ]:





# In[ ]:





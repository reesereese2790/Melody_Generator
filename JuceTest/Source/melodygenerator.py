import json
import numpy as np
import tensorflow
from tensorflow import keras
import music21 as m21
from preprocessing import SEQUENCE_LENGTH, MAPPING_PATH

class MelodyGenerator:
    
    def __init__(self, model_path="model.h5"):
        
        self.model_path = model_path
        self.model=keras.models.load_model(model_path)
        
        with open(MAPPING_PATH, "r") as fp:
            self._mappings = json.load(fp)
            
        self._start_symbols = ["/"] * SEQUENCE_LENGTH
        
    def generate_melody(self, seed, num_steps, max_sequence_length, temperature):
        #seed is "64_63__", sequence length is 4 bars in 4/4
        
        #create seed with start symbols
        seed = seed.split()
        melody = seed
        seed = self._start_symbols + seed
        
        #map seed to int
        seed = [self._mappings[symbol] for symbol in seed]
        
        for _ in range(num_steps):
            
            #limit the seed to max_sequence_length
            seed = seed[-max_sequence_length:]
            
            #one hot encode the seed
            onehot_seed = keras.utils.to_categorical(seed, num_classes=len(self._mappings))
            #(1, max_sequence_length, num of symbols in vocab)
            onehot_seed = onehot_seed[np.newaxis, ...]
            
            #make a prediction
            probabilities = self.model.predict(onehot_seed)[0]        #only first sample
            #[0.1,0.2,0.1,0.6] -> 1
            output_int = self._sample_with_temperature(probabilities,temperature)
            
            #update seed
            seed.append(output_int)
            
            #map int to encoding
            output_symbol = [k for k,v in self._mappings.items() if v == output_int][0]
            
            #check whether at end of melody
            if output_symbol == "/":
                break
                
            #update melody
            melody.append(output_symbol)
            
        return melody
            
    def _sample_with_temperature(self, probabilities, temperature):
        # temperature -> infinity, more random, nondeterministic
        # temperature -> 0 , determines prob dist, deterministic
        # temperature = 1, dont change dist,how explorative network is
        predictions = np.log(probabilities) / temperature
        probabilities = np.exp(predictions) / np.sum(np.exp(predictions))
        
        choices = range(len(probabilities)) #[0,1,2,3]
        index = np.random.choice(choices, p=probabilities)
        
        return index
    
    def save_melody(self, melody, user_key, step_duration=0.25, format="midi", file_name="mel.midi"):
        
        #create a music 21 stream
        stream = m21.stream.Stream()
        
        #parse symbols in melody and create note/rest objects
        #60_ _ _ r _ 62 _ _
        start_symbol = None
        step_counter = 1
        
        for i, symbol in enumerate(melody):
            
            #handle case in which we have a note / rest
            if symbol != "_" or i+1 == len(melody):
                
                #ensure were dealing with note/rest beyond the first one
                if start_symbol is not None:
                    
                    quarter_length_duration = step_duration * step_counter
                    
                    #handle rest
                    if start_symbol == "r":
                        m21_event = m21.note.Rest(quarterLength = quarter_length_duration)
                    
                    #handle note
                    else:
                        m21_event = m21.note.Note(int(start_symbol), quarterLength = quarter_length_duration)
                        
                    stream.append(m21_event)
                    
                    #reset the step counter
                    step_counter = 1
                    
                start_symbol = symbol
            
            #handle case where we have a prolongation sign _
            else:
                step_counter += 1
        
        #transpose to Cmaj/Amin
        if user_key == 1:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("C"))

        #transpose to C#maj
        elif user_key == 2:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("C#"))

        #transpose to Dmaj
        elif user_key == 3:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("D"))

        #transpose to D#maj
        elif user_key == 4:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("D#"))

        #transpose to Emaj
        elif user_key == 5:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("E"))

        #transpose to Fmaj
        elif user_key == 6:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("F"))

        #transpose to F#maj
        elif user_key == 7:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("F#"))

        #transpose to Gmaj
        elif user_key == 8:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("G"))

        #transpose to G#maj
        elif user_key == 9:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("G#"))

        #transpose to Amaj
        elif user_key == 10:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("A"))

        #transpose to A#maj
        elif user_key == 11:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("A#"))

        #transpose to Bmaj
        elif user_key == 12:
            interval = m21.interval.Interval(m21.pitch.Pitch("C"),m21.pitch.Pitch("B"))
        
        #transpose the stream
        transposed_stream = stream.transpose(interval)
        
        #write m21 stream to midi
        transposed_stream.write(format, file_name)
    
    
    
if __name__ == "__main__":
    
    mg=MelodyGenerator()
    
    #initialize choices
    selectedID1 = 1
    selectedID2 = 1
    selectedID3 = 1
    user_seed = selectedID1
    user_temp = selectedID2
    user_key = selectedID3
    
    #seed options
    if (user_seed == 1):
        seed = "67 _ _ _ _ 60 _ _ _ _ _ 67 _"
    elif (user_seed == 2):
        seed = "60 _ _ 65 _ 60 _ _ _ 64 _ 67 _ _ _ _"
    elif (user_seed == 3):
        seed = "60 _ 62 65 _ 60 _ 69 65 64 _ 67 _ 60 67 _"
        
    #temp options
    if (user_temp == 1):
        temperature = 0.1
    elif (user_temp == 2):
        temperature = 0.6
    elif (user_temp == 3):
        temperature = 0.9
    
    melody = mg.generate_melody(seed, 500, SEQUENCE_LENGTH, temperature)
    print(melody)
    mg.save_melody(melody,user_key)




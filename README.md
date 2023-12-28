#LSTM Melody Generator
Steps to Generate Random Melodies:
1. Download kern score data set for folk songs here: https://kern.humdrum.org/cgi-bin/browse?l=essen/europa/deutschl
2. Run preprocessing.py and func.py to preprocess dataset and create model.h5.
3. Download Juce software to create the plugin using the underlying LSTM model.
4. Run PluginEditor.h and .cpp as well as PluginProcessor.h and .cpp in the Juce shell to generate melodies.
5. Each time the plugin is called in Juce, the melodygenerator.py runs which creates random melodies.
6. A MIDI file is outputted with the random melody with user inputs of key, seed, and temperature.  

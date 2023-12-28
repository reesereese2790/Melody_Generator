/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"
#include <iostream>
#include <sstream>

#ifdef _DEBUG
    #undef _DEBUG
        #include <C:\Users\reese\Desktop\Python_Location\include\Python.h>
    #define _DEBUG
#else
    #include <C:\Users\reese\Desktop\Python_Location\include\Python.h>
#endif

//==============================================================================
JuceTestAudioProcessorEditor::JuceTestAudioProcessorEditor (JuceTestAudioProcessor& p)
    : AudioProcessorEditor (&p), audioProcessor (p)
{
    // Make sure that before the constructor has finished, you've set the
    // editor's size to whatever you need it to be.
    setSize (400, 300);
    setupUI();

    comboBox1.addItem("Longer notes", 1);
    comboBox1.addItem("Mix of notes", 2);
    comboBox1.addItem("Arpeggiated notes", 3);
    comboBox1.setBounds(10, 60, 200, 30);
    comboBox1.addListener(this);
    addAndMakeVisible(comboBox1);

    comboBox2.addItem("Less randomness", 1);
    comboBox2.addItem("Medium randomness", 2);
    comboBox2.addItem("High randomness", 3);
    comboBox2.setBounds(10, 110, 200, 30);
    comboBox2.addListener(this);
    addAndMakeVisible(comboBox2);

    comboBox3.addItem("C major", 1);
    comboBox3.addItem("C# major", 2);
    comboBox3.addItem("D major", 3);
    comboBox3.addItem("D# major", 4);
    comboBox3.addItem("E major", 5);
    comboBox3.addItem("F major", 6);
    comboBox3.addItem("F# major", 7);
    comboBox3.addItem("G major", 8);
    comboBox3.addItem("G# major", 9);
    comboBox3.addItem("A major", 10);
    comboBox3.addItem("A# major", 11);
    comboBox3.addItem("B major", 12);
    comboBox3.setBounds(10, 160, 200, 30);
    comboBox3.addListener(this);
    addAndMakeVisible(comboBox3);

}

JuceTestAudioProcessorEditor::~JuceTestAudioProcessorEditor()
{
    downloadButton.removeListener(this);
}

//==============================================================================
void JuceTestAudioProcessorEditor::paint (juce::Graphics& g)
{
    // (Our component is opaque, so we must completely fill the background with a solid colour)
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));

    g.setColour (juce::Colours::white);
    g.setFont (15.0f);
    g.drawFittedText ("This is a random melody generator. Please choose seed, temperature, and key options. \n Hit the download button to get the midi file on your Desktop.", getLocalBounds().removeFromTop(40), juce::Justification::centred, 1);
}

void JuceTestAudioProcessorEditor::resized()
{
    // This is generally where you'll want to lay out the positions of any
    // subcomponents in your editor..
}

void JuceTestAudioProcessorEditor::comboBoxChanged(juce::ComboBox* comboBoxThatHasChanged)
{
    if (comboBoxThatHasChanged == &comboBox1)
    {
        selectedID1 = comboBox1.getSelectedId();
        juce::String selectedText1 = comboBox1.getText();
    }

    else if (comboBoxThatHasChanged == &comboBox2)
    {
        selectedID2 = comboBox2.getSelectedId();
        juce::String selectedText2 = comboBox2.getText();
    }

    else if (comboBoxThatHasChanged == &comboBox3)
    {
        selectedID3 = comboBox3.getSelectedId();
        juce::String selectedText3 = comboBox3.getText();
    }
}

int JuceTestAudioProcessorEditor::runPythonScript(int input1, int input2, int input3)
{
    Py_Initialize();

    // Construct the command to run the Python script with arguments
    std::stringstream command;
    command << "python C:/Users/reese/Documents/JuceTest/JuceTest/Source/func.py " << input1 << " " << input2 << " " << input3;

    // Run the Python script with arguments using system command
    int status = system(command.str().c_str());

    if (status != 0) {
        std::cerr << "Error running Python script." << std::endl;
    }

    Py_Finalize();

    return status;
}

void JuceTestAudioProcessorEditor::buttonClicked(juce::Button* button)
{
    if (button == &downloadButton)
    {
        int status = runPythonScript(selectedID1, selectedID2, selectedID3);
    }
}

void JuceTestAudioProcessorEditor::setupUI()
{
    // Set up the Download Button
    addAndMakeVisible(downloadButton);
    downloadButton.setBounds(10, 210, 150, 30);
    downloadButton.setButtonText("Download File");
    downloadButton.addListener(this);
}


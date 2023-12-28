/*
  ==============================================================================

    This file contains the basic framework code for a JUCE plugin editor.

  ==============================================================================
*/

#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

//==============================================================================
/**
*/
class JuceTestAudioProcessorEditor  : public juce::AudioProcessorEditor, private juce::ComboBox::Listener, private juce::Button::Listener
{
public:
    JuceTestAudioProcessorEditor (JuceTestAudioProcessor&);
    ~JuceTestAudioProcessorEditor() override;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;
    void buttonClicked(juce::Button* button) override;

private:
    // This reference is provided as a quick way for your editor to
    // access the processor object that created it.
    int runPythonScript(int input1, int input2, int input3);
    int selectedID1 = 0;
    int selectedID2 = 0;
    int selectedID3 = 0;
    JuceTestAudioProcessor& audioProcessor;
    juce::ComboBox comboBox1;
    juce::ComboBox comboBox2;
    juce::ComboBox comboBox3;
    void comboBoxChanged(juce::ComboBox* comboBoxThatHasChanged) override;

    void setupUI();
    juce::TextButton downloadButton;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (JuceTestAudioProcessorEditor)
};

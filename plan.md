This project will create a cross-platform desktop app that runs pytorch machine learning models and allows users to train models in an active learning loop. 

Conda environment: `conda activate train_gui`

The project will use the bioacoustics model zoo for pre-trained bioacoustic identification models: https://github.com/kitzeslab/bioacoustics-model-zoo/

and opensoundscape: https://github.com/kitzeslab/opensoundscape which uses pytorch

The front end will be fluid, modern, intuitive, and attractive. 

Users can customize preprocessing, training, and inference settings. These settings are saved and loaded from configuration files. Python scripts for pytorch model inference and training run in subprocesses and reference the configuration files. 

The app will be built for desktop guis on Mac, Linux, and Windows. Python environments will be bundled and shipped to the user. Users should simply be able to install and launch the app, then use GUI workflows for model training and inference. 

streamlit_inference.py is provided as a reference for understanding and porting basic functionality, but not as a final product. 



# Visual design

For theming, let's switch to using Material UI components and theming throughout
Installation: (I ran this myself)
npm install @mui/material @emotion/react @emotion/styled

Use default light color theme, for now. 

For fonts let's switch to Monserrat, via FontSource
npm install @fontsource/monserrat
Then you can import it in your entry point like this:
import '@fontsource/monserrat/300.css';
import '@fontsource/monserrat/400.css';
import '@fontsource/monserrat/500.css';
import '@fontsource/monserrat/700.css';


Review tab visuals:
- dB range slider still has poor appearance. use the react material-ui range slider
- also throughout, switch to using the AutoComplete element from material-ui for multi-selects . example:
<Autocomplete
        multiple
        id="tags-outlined"
        options={speciesList}
        getOptionLabel={(option) => option.title}
        defaultValue={[speciesList]}
        renderInput={(params) => (
          <TextField
            {...params}
            label="select species"
            placeholder="Selected labels"
          />
        )}
      />



previous color scheme:
but these colors for accents: 
#eae0d5 off-white shades
#395756 dark accent 1
#4f5d75 dark accent 2
#c6ac8f medium accent
#d36135 highlights/alert


# Review tab:
User will select an annotation task. The interface will be very similar to that implemented in backend/reference/binary_classification_review.py:
- the annotation task is a csv with the relative audio path `file`, `start_time` in seconds of the clip within the audio path, `annotation`, and `comments`
- grid of spectrogram/audio clip cards displayed to user, with pagination over all rows in the annotation task
- there will be two review modes: binary review and multi-class review
- binary review: as in binary_classification_review.py, there is a multi-select for 'yes' 'no' 'unsure' or 'unlabeled' for each audio clip. A visual effect (eg colored outline green/yellow/red/grey) indicates the current label of the clip. Optionally, the user can toggle on "show comment field" and write text comments. `annototation` value is yes/no/unsure or empty (nan) for not annotated
- multi-class review: each audio clip panel has multi-select (react-select) instead of multi-select of yes/no/unsure/unlabeled. `annotation` column will contain a comma-separated list of classes ['a','b']. Empty list [] indicates annotated and no classes, whereas empty / nan indicates the clip has not been annotated. 
- implement a settings panel with spectrogram window length, frequency bandpass range, dB range, colormap, number of rows and columns for grid of displayed clips, show/hide comments field, show/hide file name

## Shortcuts for review tab (when in grid view):
- generally, use ctrl for window and cmd for mac
- toggle shortcuts on/off in the settings tab
- ctrl/cmd+shift+C: show/hide comments
- ctrl/cmd+A/S/D/F: annotate all clips on page as yes/no/uncertain/unlabeled (only has an effect in binary classification model)
- ctrl+j/k: previous/next page 


## Filtering by annotation for review tab
- in the left tray, add a multi-select box for filtering by annotation
- in binary review mode, filters by `annotation`, and a checkbox to enable/disable filtering
- in multi-class review mode, provides two filter multi-selects: filter by label with enable/disable, and filter by annotation status with enable/disable



# Incomplete items:

## Review tab issues
- filtering or changing number of displayed spectrograms should cause a re-fetch of spectrograms. Currently, if new items are displayed the spectrograms are not rendered, and user sees blank panels after filtering or increasing number of visible samples. These two actions shoudl trigger re-fetch just like pagination does. 
- exporting annotations still has two sequential file selection dialogues
- all colormaps still result in greyscale spectrograms, but some should result in colored images. The colormaps were working previously but now colormaps except 'inverted grayscale' all look like black with white for the sounds. Add debugging information for this since this issue has been difficult to crack
- root audio folder no longer auto-populates after selecting annotation task csv. It should auto-populate to the same folder as the selected csv, if it is currently empty. 
- if no annotation file is currently loaded, add a "Load annotation csv" button in the main window (exactly like the button in the left panel)

- the multi-selects for filtering should use the same type of selector as the annotation panels, react-select

# feature requests
- throughout the application, when providing click-to-play spectrograms, make it so that clicking on the left 20% of the spectrogram rewinds the clip to the beginning instead of performing the play/pause action. Show a rewind icon when hovering over the left 20% of the spectrogram. 

## create annotation tasks: 
from wizard or from review tab
filter to date and time ranges
stratification by metadata columns, date
select score range or stratified score bins for random sample, or top N


## Focus mode for review tab
- provide a toggle at the top of the review page to switch between viewing lots of clips on a page (current setup) and viewing a single, large spectrogram (click to play) in 'focus' mode.
- in focus mode, offer these shortcuts for binary classification mode: "a" = yes, "s" = no, "d" = unsure, "f" = unlabeled. "j" view previous, "k" view next clip. spacebar to play/pause audio. 
- in focus mode, auto-advance to next clip when user clicks or uses shortcut to provide an annotation of yes/no/unknown/unlabeled
- in settings panel, add a check box for whether to auto-play clips when using focus mode. When checked, the audio begins as soon as the spectrogram is displayed. 

## training!

# TODO

# updates to focus mode for review tab
- toggle review vs grid layout with Escape key
- disable keyboard shortcuts a/s/d/f/j/k/spacebar when any text field is focused (eg comments, settings fields)
e.g. check:
const isTyping = (
                    e.target.tagName === "TEXTAREA" ||
                    (e.target.tagName === "INPUT" && e.target.type === "text")
                );

## layout of review tab
- rather than using a panel within the main window, use the entire main window 
- buttons for expanding the left and right trays, switching between focus/grid mode, toggling comment visibility, and page navigation all fit neatly at the top of the main window; also add buttons for "Open" and "Save" annotation files, using symbols rather than text.  
- we don't need any headers for "review annotations" or "Annotation Review"


## auto-save for review tab
- create a session variable for where to save annotations
- add a toggle/button switch for auto-save on/off, default on
- user selects the save location with a button
- any time the user changes page or goes to previous/next clip in focus mode, auto-saves if auto-save is on
- if save location has not been set, opens a File Save As dialogue to select the file


## Review tab Focus view refinements
- compact the controls: file name, annotation buttons, audio playback, comments, and forward/backward should all be smaller and be located neatly beneath the spectrogram view 

## inference updates:
- refactor as "create inference task" -> task gets a name, and same options as the app currently has, then launches background task and monitors progress in a pane that monitors each task. API is not disabled, instead user can create additional inference tasks that will run after the running one is complete. Tasks pane monitors completed, running, and queued prediction tasks
- subset classes: can use text file or ebird filter
- optional sparse outputs: don't save scores below a floor, and save df as a sparse pickle

- TODO: better progress reporting, currently goes from 0-100 instantly
- TODO: smart segmenting into subtasks for large prediction tasks, with intermittent saving


# Explore tab updates
- remove "Score Distribution" text from the panel headings
- when you click on a histogram bar, it says "click to load spectrogram" but should instead say "loading spectrogram...". Remove the dumb little speaker icon also. 
- should have a little button in the panel (gold medal icon?) to return to viewing the highest-scoring clip (eg after clicking on a histogram bin)
- put the settings in a side panel, exactly like the settings in the review tab



## plan for initial share-able desktop app
- package the app as a desktop app in whatever way will be easy to  share with users on Windows + Mac, and be robust to cross platform issues
- include one Python environment with all required packages 
- only include those models in the bioacoustics model zoo which don't require TensorFlow (exclude: Perch, BirdNET, and )

## long-term plan for shipping environments for BMZ models
- build a set of a few environments necessary to run bmz models
- only download the required env on-demand
- if not running bmz models/training, user has light weight env for backend, and can do annotation tasks without heavy PyTorch env

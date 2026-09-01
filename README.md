epoc eeg signal viewer
======================

EPOC Headset basic EEG capture and visualization app.  
Originally created as a quick-and-dirty command-line logger, it has evolved into a **Windows desktop application with a graphical user interface (GUI)**.

This Visual Studio project builds a **32-bit Windows desktop app** that:

* Connects to an **Emotiv EPOC** headset.
* Picks up the EEG stream from the device.
* Shows the **AF3 channel** signal in real time.

The application can also generate log files that are compatible with the MATLAB helper function shown below.

Building
========

1. Open the Visual Studio solution (`.sln`) included in this repository.
2. Make sure the project is configured to build for **Win32 / x86 (32-bit)**:
   * In Visual Studio, select:  
     **Build → Configuration Manager…**  
     and set *Active solution platform* to **Win32**.
3. Build the project:
   * **Build → Build Solution**.

> **Important:**  
> The Emotiv Research Edition SDK used by this project is **32-bit only**.  
> You **must** compile the app as a 32-bit executable; otherwise it will not work and you will likely run into hard-to-debug issues.

Running
=======

1. Connect and power on your **Emotiv EPOC** headset.
2. Launch the `epoc eeg viewer` Windows application (the built `.exe`).
3. The AF3 sensor will be displayed in real time.
4. Use the up and down arrows to set the desired blink thresohld detection. 

Dependencies
============

* Windows 7  
* **EEG EPOC Emotiv Research Edition SDK for Windows (32-bit)**  
* Visual Studio (for building the project)

Matlab
======

Additionally, you can import the generated `.dat` files into MATLAB using the following function:

```matlab
function output = loadepoceegrawbyfile(fullfile, dowemean)

    fid = fopen(fullfile);

    output_matrix = fscanf(fid, ...
        '%f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f', ...
        [22 inf]);

    fclose(fid);

    output_matrix = output_matrix';
    output = output_matrix(:, 2:15);   % keep the 14 EEG channels

    if (dowemean == 1)
        [n, ~] = size(output);
        output = output - ones(n,1) * mean(output, 1);
    end
end

```

Data analysis
=============

The `data analisys/` folder holds the Python scripts that turn the recorded sessions
into the figures of the report. The recordings themselves live in `data analisys/studies/`.

Requirements: Python 3 with `numpy`, `pandas`, `matplotlib` and `scipy`.

```
pip install numpy pandas matplotlib scipy
```

**General rule:** run each script from inside `data analisys/`. Each one reads its
sessions from `studies/` and writes its PNG straight into the report's `02_Images/`.

```
cd "data analisys"
python coupling_figure.py
```

| Script | Figure produced |
| --- | --- |
| `sample_jitter.py` | `SampleToSample` |
| `batch_jitter.py` | `SyncResponseTime` / `SyncResponseTimeSleep` |
| `batch_jitter_bell.py` | `SyncLatency_Normal_*` |
| `sync_quantization.py` | `SyncQuantization` |
| `goertzel_ovelayed.py` | `LatencyOverlayed` |
| `goertzel_compare.py` | `LatencyCompare`, `LatencyCompareDelay` |
| `coupling_figure.py` | `CouplingExample`, `CouplingAmplitude` |
| `wavgen.py`, `wavgen_stereo.py` | the 16 Hz stimulus `.wav` files |

Two exceptions to the rule above:

* `batch_jitter.py` has two modes (with / without pacing), selected by commenting
  the corresponding input path and `savefig` line.
* `sync_quantization.py` uses relative paths and writes its PNG to the current
  directory, so it must be run from `data analisys/` and the figure copied by hand.

Authors
=======
Gabriel Silvatici

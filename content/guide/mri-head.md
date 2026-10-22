Title: How to read an MRI head
Emoji: 🧲
Description: What each sequence is for, in one line each, and a short order to look at them in.
Group: core
Order: 50
Draft: true

!!! note "tl;dr:"
    **T1 is for anatomy and contrast. T2 and FLAIR are for water. DWI is for crowding. SWI and GRE are for metal.**<br>
    Decide what question you are asking, then look at the sequence that answers it.

If CT is a looking glass into the brain, MRI is a microscope. It shows far more, which is exactly why it is confusing: one study arrives as a stack of eight or ten sequences, each a different shade of grey, and the radiologist talks about "T2 prolongation" and "T1 shortening" as if that meant something. It does. Each sequence is tuned to a different property of tissue, so each one answers a different question. Learn the four jobs below and you can read most of a brain MRI without the report.

This chapter is the quick version. Sequence physics and the harder patterns are for a later section.

## The four jobs 🧰

| Sequence | Job | How to recognise it | Bright means |
|---|---|---|---|
| **T1** | Anatomy, and contrast | Grey matter is grey, white matter is white, CSF is black. Looks like a brain | Fat, subacute blood, melanin, protein, gadolinium |
| **T2** | Water | CSF is bright white; grey matter brighter than white matter | Oedema, gliosis, most pathology |
| **FLAIR** | Water, with the CSF switched off | Looks like T2 but the ventricles are black | Oedema next to CSF (periventricular, cortical), subarachnoid abnormality |
| **DWI** (with ADC) | Crowding | Grainy, low resolution, grey brain | Restricted diffusion: acute infarct, abscess, dense tumour, clot |
| **SWI / GRE** | Metal | Veins are dark lines; bone and air edges are messy | Nothing is bright: blood and calcium are **black** |

### T1: anatomy and contrast 🗺️

T1 is the sequence where the brain looks like the brain. Use it to find your landmarks, check the midline, and look at the pituitary and the orbits. It is also the sequence that contrast is given on. Gadolinium cannot cross an intact blood-brain barrier, so normal brain does not enhance, but tumours, abscess walls and active inflammation have no barrier and light up. If a lesion enhances, it is something that has broken the barrier.

Remember it as *number one*: anatomy is the number one thing you need to know, and a mass is the number one thing you do not want to miss.

### T2 and FLAIR: water 💧

Almost everything that goes wrong in the brain adds water, and water is bright on T2. Oedema, gliosis, demyelination, infection and tumour all show as T2 "hyperintensity". T2 tells you *something is there*; it rarely tells you what.

FLAIR is a T2 with the free water in the CSF suppressed, so the ventricles and sulci go black while oedema stays bright. That is why it is the sequence for lesions next to CSF: periventricular plaques in MS, cortical signal in encephalitis, and the "dirty" sulci of subarachnoid blood or meningitis. Remember it as *H₂O has a 2 in it*: T2 is for water.

### DWI: crowding 🚦

Diffusion imaging measures how freely water molecules can move. Anything that crowds the extracellular space traps water and shows bright on DWI with a matching dark area on the ADC map. That pairing is "restricted diffusion".

The classic cause is **acute infarct**. Ischaemic cells run out of ATP, the sodium-potassium pump fails, water rushes in, the cells swell and fill the interstitium, and water can no longer move. DWI is positive within minutes and stays bright for about a week to ten days.

But not all that glitters is gold. Three other things crowd the space:

- **Densely cellular tumour** (lymphoma, medulloblastoma, high-grade glioma): water is trapped between packed cells. These enhance, which an infarct does not in the first days.
- **Clotted blood**: fibrin mesh traps water. Also bright on CT and dark on SWI.
- **Pus**: thick and gelatinous. A ring-enhancing lesion whose *centre* restricts is an abscess, because necrotic tumour centres are liquid and do not restrict.

!!! warning "Always check the ADC"
    Anything very bright on T2 can bleed through onto DWI ("T2 shine-through") without any true restriction. True restriction is bright on DWI **and** dark on ADC. If the ADC is bright or normal, it is not an acute infarct.

### SWI and GRE: metal 🧲

Gradient echo (GRE) and its sharper cousin susceptibility-weighted imaging (SWI) are tuned to local distortions of the magnetic field, which is what metals do. The metal that matters in the brain is the iron in blood, so this is the blood sequence: haemorrhage of any age, microbleeds, haemosiderin staining and cavernomas all show as black "blooming" dots and blobs.

Remember it as *BLACKsmith*: a blacksmith works metal, and metal is black on gradient imaging. But other metals are black too, most often calcium, so a black focus is blood *or* calcium (a phase map or the CT separates them).

## A short read 📋

1. **Scout on T1 or T2.** Midline, ventricles, any obvious mass, extra-axial collection or shift.
2. **DWI, then ADC.** Anything bright? Is it dark on ADC? If yes: infarct, abscess, dense tumour or clot. Match it to the deficit you examined.
3. **FLAIR.** Where is the oedema and what shape is it? Vascular territory (wedge, cortex and white matter together), periventricular and ovoid (demyelination), medial temporal (encephalitis), vasogenic finger-like white-matter oedema around a mass.
4. **SWI or GRE.** Any black? Haemorrhagic transformation of your infarct, microbleeds, a cavernoma, calcification.
5. **Post-contrast T1.** Does anything enhance? Ring, nodular, leptomeningeal, or along the cortex.
6. **The rest.** Orbits, pituitary, skull base, the top cervical cord on the sagittal, the mastoids and sinuses.

!!! tip "Say what you see in sequence language"
    "A left MCA-territory lesion that restricts on DWI with low ADC, bright on FLAIR, with a few dark foci on SWI" says *acute infarct with early haemorrhagic transformation* to anyone who reads scans, and it is a safer sentence than a diagnosis you cannot defend.

## Three patterns you will meet in your first month 🔁

| Pattern | DWI / ADC | T2 / FLAIR | SWI | Contrast |
|---|---|---|---|---|
| **Acute infarct** | Bright / dark | Normal in the first hours, then bright | Dark only if it bleeds | Little in the first days |
| **Abscess** | Centre bright / dark | Bright centre, lots of surrounding oedema | Dark rim sometimes | Smooth ring |
| **High-grade tumour** | Variable, bright if cellular | Bright, vasogenic oedema | Dark foci of blood | Irregular ring or solid, nodular |

!!! note "DWI-FLAIR mismatch"
    A stroke that is bright on DWI but not yet on FLAIR is probably under 4.5 hours old. That is how MRI picks wake-up and unknown-onset strokes for thrombolysis. If the FLAIR is already bright, the clock has probably run out.

## What to ask for when ordering 📝

Say what question you want answered, not which sequences you want. "Stroke protocol" gets DWI, FLAIR, SWI and a time-of-flight MRA. "Tumour" or "infection" gets contrast. "Demyelination" gets a sagittal FLAIR and usually the cord. If you want the pituitary or the internal auditory meatus say so: they need their own thin slices.

!!! tip "More detail"
    The longer notes are in neuro-learn under *Cerebrovascular › Acute Ischaemic Stroke › Assessment & Stroke Imaging › Stroke Imaging › MRI* and the neighbouring *Stroke MRI Signal Evolution (DWI/ADC/T2/T1 Timeline)* page.

*Adapted from Lea Alhilali's "How to read an MRI" thread in Radiopaedia's* Neuroradiology Threads *course, with the mnemonics kept and the pictures described rather than reproduced. The sequence table, the read order and the patterns table are additions.*

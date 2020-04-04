# Chemical data for all your elements need
### Localized, extended periodic table and more in multiple formats
***

### Goal

The goal of this project is to facilitate easy to use data regarding chemical subjects such as the periodic table. Any and all contribution to add more data to the project is welcome.

For an actual usable library using this data, take a look at [MolecularJS](https://github.com/AlexGustafsson/MolecularJS).


### Available data

As of now, this repository contains data for the periodic table in regard to elements. There are also data for elementary particles. The available elements have been translated to a multitude of languages.

##### Elements

The file named `elements` contains a series of elements in the following format. The example is in JSON and shows the Hydrogen element.

```json
"number": 1,
"symbol": "H",
"name": "Hydrogen",
"mass": 1.00794,
"cpkHexColor": "FFFFFF",
"electronConfiguration": 1,
"electronNegativity": 2.2,
"radius": 37,
"ionRadius": null,
"vanDelWaalsRadius": 120,
"ionizationEnergy": 1312,
"electronAffinity": -73,
"oxidationStates": [-1, 1],
"standardState": "gas",
"bondingType": "diatomic",
"meltingPoint": 14,
"boilingPoint": 20,
"density": 0.0000899,
"family": "nonmetal",
"yearDiscovered": 1766
```

| quantity | unit | symbol |
|---|---|---|
| mass | grams per cubic centimeter | g/cm<sup>3</sup> |
| melting / boiling point | kelvin | k |
| radius | piko meters | pm |

##### Localized elements

Each element has been translated to 30 languages. All of which are available in the `elementsLocale` file. Each locale is named after the two characters long language code (i.e. 'en' for English). Each localized element is matched to the english word.

```json
"sv": {
  "Hydrogen": "Väte"
}
"tr": {
  "Hydrogen": "Hidrojen"
}
```

##### Elementary particles

The file `elementaryParticles` contain just that, information about elementary particles. The format is as follows:

```json
"proton": {
  "charge": 1,
  "mass": 1007276466812,
  "radius": 0.8775,
  "spin": 0.5,
  "discovered": {
    "year": 1918,
    "name": "Ernest Rutherford"
  }
}
```

| quantity | unit | symbol |
|---|---|---|
| mass | unified atomic mass unit | u |
| [spin](https://en.wikipedia.org/wiki/Spin_(physics)) | - | - |
| radius | piko meters | pm |

### Contributing

Any help with the project is more than welcome. If you're unable to add a change yourself, open an issue and let someone else take a look at it.

### Disclaimer

_The data available is not verified by a knowledgeable person after compilation. As such, there might be cases when the data is not correct. There is also the possibility of outdated data since it hasn't been updated recently._

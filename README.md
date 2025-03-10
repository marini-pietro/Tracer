# Tracer

Tracer is an all-in-one comprehensive tool designed to create and share combo and interaction sheets for Yu-Gi-Oh! decks and match-ups.  
Tracer allows users to place card images on a canvas of user-selected color and connect them with arrows to describe combo steps.  
Combo sheets can be then be exported as images or json files that can be later imported to continue editing.

## Features

- **Card Placement**: Place card images on a customizable canvas.
- **Combo Steps**: Connect cards with arrows to describe combo steps.
- **Export Options**: Export combo sheets as images or files.
- **Import Options**: Import previously saved combo sheets.

## Installation

Consult the `Releases` tab on the Github page and install the desired version with the provided instructions.

## Usage

The GUI is built to be minimal and easy to learn but other instructions such as shortcuts are written under the help tab available while editing a combo sheet.
Application may become unresponsive for a few seconds when importing ydk that contains cards not in cache (being worked on).

## Contributing

Contributions are welcome, if you want to contribute please follow these steps.

For code-related translations:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Document and comment your changes.
5. Commit your changes (`git commit -m 'Add some feature'`).
6. Push to the branch (`git push origin feature/your-feature-name`).
7. Open a pull request.

For porting-related contributions:

1. Fork the repository.
2. Create a new branch (`git checkout -b porting/os-name`).
3. Make your changes.
4. Document and comment your changes.
5. Create a `porting to os-name.md` with the changes made and the details of the OS to which you porting to.
6. Commit your changes (`git commit -m 'porting to os-name'`).
7. Push to the branch (`git push origin porting/os-name`).
8. Open a pull request.

For translation-related contributions:

1. Clone the repository.
2. Translate the text.
3. Use `translation-exporter.py` script to export all the text to a json file.
4. Open a Github issue with the lable `translation` and include the json file.
5. As soon as possible I will get to implementing the json file.

WARNING: the `translation-exporter.py` script and other languages are currently not implemented because of time costraints but will be in next versions.

All contributions regardless of the nature or amount of changes will be documented.

## Acknowledgements

- The Yu-Gi-Oh! community and other free projects like [YGOOmega](https://omega.duelistsunite.org/) that inspired this project.
- [CustomTkinter](https://github.com/tomschimansky/customtkinter).
- [YGOProDeck](https://ygoprodeck.com/) for the awesome site and API.
- [CTkColorWheel](https://github.com/Akascape/CTkColorPicker) for the color picker widget that I modified to fit the needs of the project.
- [CTkMessageBox](https://github.com/Akascape/CTkMessagebox?tab=CC0-1.0-1-ov-file).
- [CTkMenuBar](https://github.com/Akascape/CTkMenuBar?tab=readme-ov-file).
- [Level/Rank icon](https://yugipedia.com/wiki/User:Dinoguy1000/icons#Property).
- [Spell icons](https://yugipedia.com/wiki/User:Dinoguy1000/icons#Property).
- [Races icons](https://yugioh.fandom.com/wiki/Type).
- [Attribute icons](https://www.deviantart.com/aaiki/art/Hi-Res-Yugioh-Attributes-836887394).
- [Github icon](https://www.iconfinder.com/icons/211904/social_github_icon).
- [Settings icon](https://www.iconfinder.com/icons/326699/settings_icon).
- [Cross icon](https://www.iconfinder.com/icons/9104213/close_cross_remove_delete_icon).
- [Swap icon](https://www.iconfinder.com/icons/9035025/swap_vertical_icon).

## Contact

For any questions or suggestions, please open a github issue with the tag Question or Suggestion, I will get to responding as soon as possible.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) License.  
See the [LICENSE](LICENSE) file or the license [page](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode) for details.

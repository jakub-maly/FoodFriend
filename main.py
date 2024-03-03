
from llm import LLM
import ocr

from datetime import datetime
import sys
import pandas as pd
import os


# UI imports
from PyQt6.QtGui import QFont
from PyQt6 import uic, QtGui
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QLineEdit, QStackedWidget, QMainWindow, QFileDialog, QWidget, QVBoxLayout, \
    QHBoxLayout, QCheckBox, QLabel, QSpacerItem, QSizePolicy, QFormLayout
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


def delta_days(date_string: str) -> int:
    """ Calculates the difference between today and a given date.
    :param date_string: YYYY-MM-DD format date
    :return:            number of days between today and given date string
    """
    return (datetime.today() - datetime.strptime(date_string, '%Y-%m-%d')).days


def add_to_database(llm: LLM, image_filepath: str) -> pd.DataFrame:
    """ Adds entries from a receipt to the database of foodstuffs.
    :param llm:            reference to the LLM interface
    :param image_filepath: filepath for a receipt image
    """
    df = pd.DataFrame(
        [[datetime.today().strftime('%Y-%m-%d'), llm.get_item(text)]
         for text in str.split(ocr.image_to_text(ocr.enhance_image(image_filepath)),'\n') if '£' in text],
        columns=['time', 'item'])
    # df['perishable'] = df['item'].apply(lambda item: llm.is_perishable(item))
    # df['perishable']
    return df



class mainWindow(QMainWindow):
    def __init__(self, df, llm):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.df = df
        self.llm = llm

        self.ingredients = []

        self.deleteButton.setStyleSheet("background-image: url('resized_image.png');"
                                        "background-repeat: no-repeat;"
                                        "background-position: center;")

        self.recipeButton.clicked.connect(self.switch_to_recipe)
        self.deleteButton.clicked.connect(self.delete_items)
        self.addButton.clicked.connect(self.upload_receipt)

        self.fridgeScrollPane.setWidgetResizable(True)
        self.pantryScrollPane.setWidgetResizable(True)
        self.fridge_widget = QWidget(self)  # Create a widget to contain the scroll area content
        self.pantry_widget = QWidget(self) # maybe remove self
        self.fridgeScrollPane.setWidget(self.fridge_widget)
        self.pantryScrollPane.setWidget(self.pantry_widget)
        self.vertical_fridge = QVBoxLayout(self.fridge_widget)
        self.vertical_pantry = QVBoxLayout(self.pantry_widget)
        self.vertical_pantry.setSpacing(20)
        self.vertical_fridge.setSpacing(20)
        print(len(self.df))
        for i,row in self.df.iterrows():
            print(row["item"])
            item_layout = QHBoxLayout()
            #item_layout = QFormLayout()
            item_layout.setSpacing(100)
            checkbox = QCheckBox(row["item"])
            days = delta_days(row["time"])
            #label1 = QLabel(row["item"],alignment=Qt.AlignmentFlag.AlignLeft)
            font = QFont("Verdana", 12)
            checkbox.setFont(font)
            #label1.setFont(font)
            #label1.setAlignment(Qt.Alignment.AlignLeft)
            #label1.setFixedSize(50, 15)
            # spacer2 = QSpacerItem(20, 10, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            # item_layout.addItem(spacer2)
            label2 = QLabel(str(days))
            label2.setFont(font)
            item_layout.addWidget(checkbox)
            #item_layout.addWidget(label1)
            item_layout.addWidget(label2)
            #item_layout.addRow(checkbox, label2)
            if row["perishable"]:
                self.vertical_fridge.addLayout(item_layout)
            else:
                self.vertical_pantry.addLayout(item_layout)
        self.vertical_fridge.addStretch(1)
        self.vertical_pantry.addStretch(1)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.df.to_csv("database.csv", index=False)
        a0.accept()


    def delete_items(self):

        item_count_fridge = self.vertical_fridge.count() - 1
        for i in reversed(range(item_count_fridge)):
            item = self.vertical_fridge.itemAt(i)
            item_layout = item.layout()
            checkbox = item_layout.itemAt(0).widget()
            if checkbox.isChecked():
                self.df = self.df.drop(self.df[self.df['item'] == item_layout.itemAt(1).widget().text()].index)
                for x in reversed(range(2)):
                    widget = item_layout.takeAt(x).widget()
                    widget.deleteLater()
                self.vertical_fridge.removeItem(item_layout)
                item_layout.deleteLater()
                item_count_fridge = self.vertical_fridge.count()
        item_count_pantry = self.vertical_pantry.count() -1
        for i in reversed(range(item_count_pantry)):
            item = self.vertical_pantry.itemAt(i)
            item_layout = item.layout()
            checkbox = item_layout.itemAt(0).widget()
            if checkbox.isChecked():
                self.df = self.df.drop(self.df[self.df['item'] == item_layout.itemAt(1).widget().text()].index)
                for x in reversed(range(2)):
                    widget = item_layout.takeAt(x).widget()
                    widget.deleteLater()
                self.vertical_pantry.removeItem(item_layout)
                item_layout.deleteLater()

    def upload_receipt(self):
        fileName = QFileDialog.getOpenFileName(self,
                                               "Open Image", "", "Image Files (*.png *.jpg *.bmp)")

        new_df = add_to_database(self.llm, fileName[0])
        self.df = self.df.merge(new_df)

        for i,row in new_df.iterrows():
            item_layout = QHBoxLayout(self)
            checkbox = QCheckBox(self)
            days = delta_days(row["item"])
            label1 = QLabel(self, days)
            label2 = QLabel(self, row["time"])
            item_layout.addWidget(checkbox)
            item_layout.addWidget(label1)
            item_layout.addWidget(label2)
            if row["perishable"]:
                self.vertical_fridge.addLayout(item_layout)
            else:
                self.vertical_pantry.addLayout(item_layout)


    def switch_to_recipe(self):
        # Create and show the second window
        item_count_fridge = self.vertical_fridge.count() - 1
        for i in reversed(range(item_count_fridge)):
            item = self.vertical_fridge.itemAt(i)
            item_layout = item.layout()
            checkbox = item_layout.itemAt(0).widget()
            if checkbox.isChecked():
                ingredient = checkbox.text()
                self.ingredients.append(ingredient)
                checkbox.setChecked(False)


        item_count_pantry = self.vertical_pantry.count() -1
        for i in reversed(range(item_count_pantry)):
            item = self.vertical_pantry.itemAt(i)
            item_layout = item.layout()
            checkbox = item_layout.itemAt(0).widget()
            if checkbox.isChecked():
                ingredient = checkbox.text()
                self.ingredients.append(ingredient)
                checkbox.setChecked(False)

        self.recipe_window = recipeWindow(self, self.ingredients, self.llm)
        self.ingredients = []
        self.hide()
        self.recipe_window.show()


class recipeWindow(QMainWindow):
    def __init__(self, mainwindow, ingredients, llm):
        super().__init__()
        uic.loadUi("recipe.ui", self)
        self.mainwindow = mainwindow
        self.ingredients = ingredients
        self.ingredientScrollPane.setWidgetResizable(True)
        self.llm = llm
        self.recipeScrollArea.setWidgetResizable(True)
        recipe = self.llm.get_recipe(self.ingredients)
        # Create a label to display the long text
        self.label1 = QLabel(recipe)
        self.label1.setWordWrap(True)  # Enable word wrapping for the label
        font = QFont("Verdana", 12)
        self.label1.setFont(font)

        # Set the label as the widget of the scroll area
        self.recipeScrollArea.setWidget(self.label1)

        # Create a widget to contain the layout
        self.ingredient_widget = QWidget(self)
        self.ingredientScrollPane.setWidget(self.ingredient_widget)

        # Create a vertical layout for the widget
        self.ingredient_vbox_layout = QVBoxLayout(self.ingredient_widget)
        self.ingredient_vbox_layout.setSpacing(20)

        # Add labels with bullet points for each string in the list
        for string in self.ingredients:
            label_text = f"\u2022 {string}"  # Add bullet point before each string
            label = QLabel(label_text)
            font = QFont("Verdana", 12)
            label.setFont(font)

            self.ingredient_vbox_layout.addWidget(label)

        self.ingredient_vbox_layout.addStretch(1)

        self.exitRecipeButton.clicked.connect(self.switch_to_main)
        self.newRecipeButton.clicked.connect(self.extra_recipe)


    def extra_recipe(self):
        recipe = self.llm.get_recipe(self.ingredients)
        self.label1.setText(recipe)

    def switch_to_main(self):
        self.mainwindow.show()
        self.close()


def main():
    """ Application runner. """

    llm = LLM()

    df = pd.read_csv('database.csv', sep=r'\s*,\s*', skipinitialspace = True)



    # load the UI
    app = QApplication(sys.argv)
    window = mainWindow(df, llm)
    window.show()


    # window = uic.loadUi('base.ui')
    # window.background.setStyleSheet('background-image: url(background.png)')
    #
    # # hard-code the five example words
    # word_list = ['pane', 'prezzo', 'fresco/fresca', 'dolce', 'farina']
    # word_boxes = []
    #
    # # put the words into their respective text fields
    # for num, words in zip(range(1, 6), word_list):
    #
    #     # find the label element
    #     element = window.findChild(QLineEdit, f'word{num}textField')
    #
    #     # create the textbox
    #     textbox = CheckingTextBox(element, words.split('/'))
    #     word_boxes.append(textbox)
    #     element.returnPressed.connect(textbox.check_text)
    #
    # # create the audio player
    # sound_player = QMediaPlayer()
    # audio_output = QAudioOutput()
    # sound_player.setAudioOutput(audio_output)
    # audio_output.setVolume(50)
    #
    # window.userInput.returnPressed.connect(partial(
    #     handle_input,window.userInput, window.outputText, window.playSound, sound_player,
    #     llm, context))
    # window.show()

    sys.exit(app.exec())



if __name__ == '__main__':
    main()


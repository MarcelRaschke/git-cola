from PyQt4 import QtGui
from PyQt4 import QtCore

import cola
from cola import qt
from cola import qtutils
from cola import signals
from cola.prefs import diff_font
from cola.qtutils import connect_button
from cola.qtutils import critical
from cola.qtutils import information
from cola.views import standard


def create_tag(revision=''):
    """Entry point for external callers."""
    opts = TagOptions()
    if revision:
        opts.revisions.insert(0, revision)
    view = CreateTag(opts, qtutils.active_window())
    view.show()
    return view



class TagOptions(object):
    """Simple data container for the CreateTag dialog."""

    def __init__(self):
        self.revisions = ['HEAD'] + cola.model().all_branches()


class CreateTag(standard.Dialog):
    def __init__(self, opts, parent):
        standard.Dialog.__init__(self, parent=parent)
        self.opts = opts

        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowTitle(self.tr('Create Tag'))
        self.resize(506, 295)
        self.main_layt = QtGui.QVBoxLayout(self)
        self.main_layt.setContentsMargins(6, 12, 6, 6)

        # Form layout for inputs
        self.input_form_layt = QtGui.QFormLayout()
        self.input_form_layt.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)

        # Tag label
        self.tag_name_label = QtGui.QLabel(self)
        self.tag_name_label.setText(self.tr('Name'))
        self.input_form_layt.setWidget(0, QtGui.QFormLayout.LabelRole,
                                       self.tag_name_label)

        self.tag_name = QtGui.QLineEdit(self)
        self.tag_name.setToolTip(self.tr('Specifies the tag name'))
        self.input_form_layt.setWidget(0, QtGui.QFormLayout.FieldRole,
                                       self.tag_name)

        # Sign Tag
        self.sign_label = QtGui.QLabel(self)
        self.sign_label.setText(self.tr('Sign Tag'))
        self.input_form_layt.setWidget(1, QtGui.QFormLayout.LabelRole,
                                       self.sign_label)

        self.sign_tag = QtGui.QCheckBox(self)
        self.sign_tag.setToolTip(
                self.tr('Whether to sign the tag (git tag -s)'))
        self.input_form_layt.setWidget(1, QtGui.QFormLayout.FieldRole,
                                       self.sign_tag)
        self.main_layt.addLayout(self.input_form_layt)

        # Tag message
        self.tag_msg_label = QtGui.QLabel(self)
        self.tag_msg_label.setText(self.tr('Message'))
        self.input_form_layt.setWidget(2, QtGui.QFormLayout.LabelRole,
                                       self.tag_msg_label)

        self.tag_msg = QtGui.QTextEdit(self)
        self.tag_msg.setAcceptRichText(False)
        self.tag_msg.setToolTip(self.tr('Specifies the tag message'))
        self.tag_msg.setFont(diff_font())
        self.input_form_layt.setWidget(2, QtGui.QFormLayout.FieldRole,
                                       self.tag_msg)
        # Revision
        self.rev_label = QtGui.QLabel(self)
        self.rev_label.setText(self.tr('Revision'))
        self.input_form_layt.setWidget(3, QtGui.QFormLayout.LabelRole,
                                       self.rev_label)

        self.revision = QtGui.QComboBox()
        self.revision.addItems(self.opts.revisions)
        self.revision.setCurrentIndex(0)
        self.revision.setEditable(True)
        self.revision.setToolTip(self.tr('Specifies the SHA-1 to tag'))
        self.input_form_layt.setWidget(3, QtGui.QFormLayout.FieldRole,
                                       self.revision)

        # Buttons
        self.button_hbox_layt = QtGui.QHBoxLayout()
        self.button_hbox_layt.addStretch()

        self.create_button = qt.create_button(text='Create Tag',
                                              icon=qtutils.git_icon())
        self.button_hbox_layt.addWidget(self.create_button)
        self.main_layt.addLayout(self.button_hbox_layt)

        self.close_button = qt.create_button(text='Close')
        self.button_hbox_layt.addWidget(self.close_button)

        connect_button(self.close_button, self.accept)
        connect_button(self.create_button, self.create_tag)

    def sync_options(self):
        pass

    def create_tag(self):
        """Verifies inputs and emits a notifier tag message."""

        revision = unicode(self.revision.currentText())
        tag_name = unicode(self.tag_name.text())
        tag_msg = unicode(self.tag_msg.toPlainText())
        sign_tag = self.sign_tag.isChecked()

        if not revision:
            critical('Missing Revision', 'Please specify a revision to tag.')
            return
        elif not tag_name:
            critical('Missing Name', 'Please specify a name for the new tag.')
            return
        elif (sign_tag and not tag_msg and
            not qtutils.confirm('Missing Tag Message',
                                    'Tag-signing was requested but the tag '
                                    'message is empty.',
                                    'An unsigned, lightweight tag will be '
                                    'created instead.\n'
                                    'Create an unsigned tag?',
                                    'Create Unsigned Tag',
                                    default=False,
                                    icon=qtutils.save_icon())):
            return

        cola.notifier().broadcast(signals.tag, tag_name, revision,
                                  sign=sign_tag, message=tag_msg)
        information('Tag Created', 'Created a new tag named "%s"' % tag_name,
                    details=tag_msg or None)
        self.accept()

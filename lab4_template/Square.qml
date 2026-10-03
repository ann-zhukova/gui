import QtQuick 2.15

Rectangle {
    id: root
    property bool active: false
    signal clicked()

    width: 64
    height: 38
    radius: 8
    scale: active ? 0.9 : 1
    border.color: active ? "#ffffff" : Qt.darker(color, 1.25)
    border.width: active ? 4 : 2

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
    Behavior on scale { NumberAnimation { duration: 120 } }
}

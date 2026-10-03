import QtQuick 2.15

Rectangle {
    id: root
    property bool active: false
    property int thickness: 1
    property string text: thickness.toString()
    signal clicked()

    width: 40
    height: 40
    radius: 20
    color: active ? "#111111" : "#ffffff"
    border.color: active ? "#ffffff" : "#111111"
    border.width: active ? 2 : 1

    Text {
        anchors.centerIn: parent
        color: root.active ? "#ffffff" : "#111111"
        text: root.text
        font.family: "Segoe UI"
        font.weight: Font.DemiBold
    }
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
    Behavior on color { ColorAnimation { duration: 120 } }
}

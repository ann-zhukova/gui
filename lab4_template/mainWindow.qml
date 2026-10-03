import QtQuick 2.15
import QtQuick.Window 2.15
import "."

Window {
    id: root
    visible: true
    width: 1000
    height: 760
    minimumWidth: 720
    minimumHeight: 560
    color: "#1e1e2e"
    title: "ЛР 4"

    property color paintColor: "#33B5E5"
    property int thickness: 1

    Rectangle {
        id: toolbar
        anchors { left: parent.left; right: parent.right; top: parent.top; margins: 20 }
        height: 136
        radius: 12
        color: "#545454"
        border.color: "#707070"
        border.width: 1

        Column {
            anchors.centerIn: parent
            spacing: 12

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Цвет:"
                    color: "#ffffff"
                    font { family: "Segoe UI"; bold: true }
                }
                Repeater {
                    model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444"]
                    Square {
                        active: root.paintColor.toString() === color.toString()
                        color: modelData
                        onClicked: root.paintColor = color
                    }
                }
            }
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 8
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Толщина:"
                    color: "#ffffff"
                    font { family: "Segoe UI"; bold: true }
                }
                Repeater {
                    model: [1, 2, 3, 4, 5]
                    Circle {
                        active: root.thickness === thickness
                        thickness: modelData
                        onClicked: root.thickness = thickness
                    }
                }
            }
        }
    }

    Rectangle {
        id: canvasCard
        anchors {
            left: parent.left; right: parent.right
            top: toolbar.bottom; bottom: footer.top
            leftMargin: 20; rightMargin: 20; topMargin: 16; bottomMargin: 12
        }
        radius: 12
        color: "#252538"
        border.color: "#393950"
        clip: true

        Canvas {
            id: canvas
            anchors.fill: parent
            anchors.margins: 2
            property real lastX: 0
            property real lastY: 0
            property real nextX: 0
            property real nextY: 0
            property bool drawSegment: false
            property bool resetRequested: true

            onPaint: {
                var ctx = getContext("2d")
                if (resetRequested) {
                    ctx.clearRect(0, 0, width, height)
                    ctx.fillStyle = "#191927"
                    ctx.fillRect(0, 0, width, height)
                    resetRequested = false
                }
                if (drawSegment) {
                    ctx.lineWidth = root.thickness
                    ctx.lineCap = "round"
                    ctx.lineJoin = "round"
                    ctx.strokeStyle = root.paintColor
                    ctx.beginPath()
                    ctx.moveTo(lastX, lastY)
                    ctx.lineTo(nextX, nextY)
                    ctx.stroke()
                    lastX = nextX
                    lastY = nextY
                    drawSegment = false
                }
            }

            MouseArea {
                id: paintArea
                anchors.fill: parent
                cursorShape: Qt.CrossCursor
                onPressed: {
                    canvas.lastX = mouseX
                    canvas.lastY = mouseY
                }
                onPositionChanged: {
                    if (!pressed)
                        return
                    canvas.nextX = mouseX
                    canvas.nextY = mouseY
                    canvas.drawSegment = true
                    canvas.requestPaint()
                }
            }
        }
    }

    Rectangle {
        id: footer
        anchors { left: parent.left; right: parent.right; bottom: parent.bottom; margins: 20 }
        height: 54
        color: "transparent"

        Text {
            id: saveStatus
            anchors { left: parent.left; verticalCenter: parent.verticalCenter }
            width: parent.width - actions.width - 28
            elide: Text.ElideMiddle
            color: "#aaa7c2"
            text: "Автосохранение каждые 10 секунд"
            font.family: "Segoe UI"
        }

        Row {
            id: actions
            anchors { right: parent.right; verticalCenter: parent.verticalCenter }
            spacing: 10

            Rectangle {
                width: 112; height: 42; radius: 8
                color: clearMouse.containsMouse ? "#44445f" : "#34344b"
                border.color: "#4b4b68"
                Text { anchors.centerIn: parent; text: "Очистить"; color: "white"; font.family: "Segoe UI" }
                MouseArea {
                    id: clearMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        canvas.resetRequested = true
                        canvas.requestPaint()
                        saveStatus.text = "Холст очищен"
                    }
                }
            }
            Rectangle {
                width: 128; height: 42; radius: 8
                color: saveMouse.containsMouse ? "#58c9ed" : "#33B5E5"
                Text { anchors.centerIn: parent; text: "Сохранить"; color: "white"; font.family: "Segoe UI"; font.weight: Font.DemiBold }
                MouseArea {
                    id: saveMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: _backend.request_save()
                }
            }
        }
    }

    Connections {
        target: _backend
        function onSaveRequested(filePath) {
            var result = canvas.save(filePath)
            if (result === true) {
                _backend.save_completed(filePath, true)
                return
            }
            // На некоторых графических бэкендах Canvas.save() может вернуть
            // false. В этом случае сохраняем снимок Item тем же GUI-потоком.
            var captureStarted = canvas.grabToImage(function(image) {
                _backend.save_completed(filePath, image.saveToFile(filePath))
            })
            if (!captureStarted)
                _backend.save_completed(filePath, false)
        }
        function onSaved(filePath) { saveStatus.text = "Сохранено: " + filePath }
        function onSaveFailed(message) { saveStatus.text = message }
        function onStatusChanged(message) { saveStatus.text = message }
    }

    // Резервный QML-таймер вызывает тот же бэкенд. Python объединяет события,
    // пришедшие одновременно от QTimer и этого таймера.
    Timer { interval: 1000; running: true; repeat: false; onTriggered: _backend.request_save() }
    Timer { interval: 10000; running: true; repeat: true; onTriggered: _backend.request_save() }

    Component.onCompleted: {
        canvas.requestPaint()
    }
}

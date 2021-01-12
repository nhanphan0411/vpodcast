console.log("Hello")

const uploadFile = document.getElementById("file-upload")

uploadFile.addEventListener("input", (e) => {
    const fileName = document.getElementById("file-name")
    fileName.innerHTML = uploadFile.value
})
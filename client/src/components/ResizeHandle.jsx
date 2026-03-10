import { useRef, useCallback } from 'react'
import './ResizeHandle.css'

export default function ResizeHandle({ onResize }) {
    const handleRef = useRef(null)

    const onMouseDown = useCallback((e) => {
        e.preventDefault()
        const startX = e.clientX

        const onMove = (e) => {
            const dx = e.clientX - startX
            onResize(dx)
        }

        const onUp = () => {
            document.removeEventListener('mousemove', onMove)
            document.removeEventListener('mouseup', onUp)
            document.body.style.cursor = ''
            document.body.style.userSelect = ''
            handleRef.current?.classList.remove('active')
        }

        document.addEventListener('mousemove', onMove)
        document.addEventListener('mouseup', onUp)
        document.body.style.cursor = 'col-resize'
        document.body.style.userSelect = 'none'
        handleRef.current?.classList.add('active')
    }, [onResize])

    return (
        <div
            ref={handleRef}
            className="resize-handle"
            onMouseDown={onMouseDown}
        />
    )
}

import React, { useState } from 'react'
import axios from 'axios'

const App = () => {
  const [a, setA] = useState('')
  const [b, setB] = useState('')
  const [result, setResult] = useState('')

  const calculate = async (op) => {
    const res = await axios.post('http://localhost:5000/calculate', {
      a: Number(a),
      b: Number(b),
      op
    })
    setResult(res.data.result)
  }

  return (
    <div style={{padding: 40}}>
      <h1>Calculator</h1>
      <input value={a} onChange={e => setA(e.target.value)} />
      <input value={b} onChange={e => setB(e.target.value)} />
      <br/><br/>
      <button onClick={() => calculate('add')}>+</button>
      <button onClick={() => calculate('subtract')}>-</button>
      <button onClick={() => calculate('multiply')}>*</button>
      <button onClick={() => calculate('divide')}>/</button>
      <h2>Result: {result}</h2>
    </div>
  )
}

export default App
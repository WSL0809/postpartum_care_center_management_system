use aes_gcm::{
    aead::{Aead, NewAead},
    Aes256Gcm, Nonce,
};
use pyo3::types::PyBytes;
use pyo3::wrap_pyfunction;
use pyo3::{exceptions::PyValueError, prelude::*};
use rand::Rng;

#[pyfunction]
fn encrypt(py: Python, data: Vec<u8>, key: Vec<u8>) -> PyResult<PyObject> {
    if key.len() != 32 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Invalid key length",
        ));
    }

    let cipher = Aes256Gcm::new_from_slice(&key).unwrap();

    let mut rng = rand::thread_rng();
    let nonce: [u8; 12] = rng.gen();
    let nonce = Nonce::from_slice(&nonce);

    let encrypted_data = match cipher.encrypt(nonce, data.as_ref()) {
        Ok(enc) => enc,
        Err(_) => {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Encryption failed",
            ))
        }
    };

    let mut result = nonce.as_slice().to_vec();
    result.extend_from_slice(&encrypted_data);

    Ok(PyBytes::new(py, &result).into())
}

#[pyfunction]
fn decrypt(py: Python, encrypted_data_with_nonce: Vec<u8>, key: Vec<u8>) -> PyResult<PyObject> {
    if key.len() != 32 {
        return Err(PyErr::new::<PyValueError, _>("Invalid key length"));
    }

    if encrypted_data_with_nonce.len() < 12 {
        return Err(PyErr::new::<PyValueError, _>("Invalid data"));
    }
    let (nonce_bytes, encrypted_data) = encrypted_data_with_nonce.split_at(12);
    let nonce = Nonce::from_slice(nonce_bytes);

    let cipher = Aes256Gcm::new_from_slice(&key).unwrap();

    let decrypted_data = match cipher.decrypt(nonce, encrypted_data) {
        Ok(dec) => dec,
        Err(_) => return Err(PyErr::new::<PyValueError, _>("Decryption failed")),
    };

    Ok(PyBytes::new(py, &decrypted_data).into())
}

#[pymodule]
fn cryption(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(encrypt, m)?)?;
    m.add_function(wrap_pyfunction!(decrypt, m)?)?;
    Ok(())
}

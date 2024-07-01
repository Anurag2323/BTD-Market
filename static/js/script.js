document.getElementById('productImageFile').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function() {
            const imagePreview = document.getElementById('imagePreview');
            imagePreview.src = reader.result;
            imagePreview.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
});

document.getElementById('productImageUrl').addEventListener('input', function(event) {
    const url = event.target.value;
    if (url) {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = url;
        imagePreview.style.display = 'block';
    }
});

document.getElementById('product-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const productId = document.getElementById('productId').value;
    if (productId) {
        updateProduct(productId);
    } else {
        addProduct();
    }
});

function addProduct() {
    const productName = document.getElementById('productName').value;
    let productImage = document.getElementById('productImageFile').files[0];
    const productImageUrl = document.getElementById('productImageUrl').value;

    if (productImageUrl) {
        productImage = productImageUrl;
    } else if (productImage) {
        const reader = new FileReader();
        reader.onload = function() {
            productImage = reader.result;
            submitProduct('add', null, productName, productImage);
        }
        reader.readAsDataURL(productImage);
        return;
    } else {
        alert('Please provide a product image.');
        return;
    }

    submitProduct('add', null, productName, productImage);
}

function updateProduct(id) {
    const productName = document.getElementById('productName').value;
    let productImage = document.getElementById('productImageFile').files[0];
    const productImageUrl = document.getElementById('productImageUrl').value;

    if (productImageUrl) {
        productImage = productImageUrl;
    } else if (productImage) {
        const reader = new FileReader();
        reader.onload = function() {
            productImage = reader.result;
            submitProduct('update', id, productName, productImage);
        }
        reader.readAsDataURL(productImage);
        return;
    } else {
        productImage = document.getElementById('imagePreview').src;
    }

    submitProduct('update', id, productName, productImage);
}

function submitProduct(action, id, name, image) {
    const productPrice = parseFloat(document.getElementById('productPrice').value);
    const productUnits = parseInt(document.getElementById('productUnits').value);
    const unitPrice = (productPrice / productUnits).toFixed(2);

    const product = {
        name: name,
        image: image,
        price: productPrice,
        units: productUnits,
        unit_price: unitPrice
    };

    let url = '/add_product';
    if (action === 'update') {
        url = `/update_product/${id}`;
        product.position = id; // keep the position the same when updating
    } else {
        // For new product, set the position to be the next in sequence
        const products = document.querySelectorAll('.product-item');
        product.position = products.length;
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.reload();
        }
    });
}

function editProduct(id) {
    fetch(`/get_product/${id}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('productId').value = data.id;
        document.getElementById('productName').value = data.name;
        document.getElementById('productPrice').value = data.price;
        document.getElementById('productUnits').value = data.units;
        document.getElementById('imagePreview').src = data.image;
        document.getElementById('imagePreview').style.display = 'block';
    });
}

function deleteProduct(id) {
    fetch(`/delete_product/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.reload();
        }
    });
}

// Initialize Sortable
const productCatalog = document.getElementById('productCatalog');
const sortable = new Sortable(productCatalog, {
    animation: 150,
    onEnd: function () {
        const productOrder = [];
        document.querySelectorAll('.product-item').forEach((item, index) => {
            productOrder.push(item.dataset.id);
        });

        fetch('/reorder_products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productOrder)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.reload();
            }
        });
    }
});

import torch
import timm
from torchvision import transforms
from PIL import Image
import numpy as np
import cv2
import base64

LABELS = [
    'Atelectasis', 'Cardiomegaly', 'Consolidation',
    'Edema', 'Enlarged Cardiomediastinum', 'Fracture',
    'Lung Lesion', 'Lung Opacity', 'No Finding',
    'Pleural Effusion', 'Pleural Other', 'Pneumonia',
    'Pneumothorax', 'Support Devices'
]

IMG_SIZE = 224

resize = transforms.Resize((IMG_SIZE, IMG_SIZE))
to_tensor = transforms.ToTensor()
normalize = transforms.Normalize(
    mean=[0.485, 0.456, 0.406],
    std=[0.229, 0.224, 0.225]
)


def load_image_model(model_path):
    device = torch.device("cpu")

    model = timm.create_model(
        'swin_base_patch4_window7_224',
        pretrained=False,
        num_classes=len(LABELS)
    )

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    return model


def generate_gradcam_heatmap(model, image_tensor, original_image, target_class):
    features = []
    gradients = []
    
    def save_features(module, input, output):
        features.append(output)
        
    def save_gradients(module, grad_in, grad_out):
        # Use grad_out[0] for full_backward_hook as well
        gradients.append(grad_out[0])
        
    # Use Stage 3 (layers[2]) for a good balance of resolution and features
    target_layer = model.layers[2].blocks[-1]
    
    handle_f = target_layer.register_forward_hook(save_features)
    handle_b = target_layer.register_full_backward_hook(save_gradients)
    
    out = model(image_tensor)
    
    model.zero_grad()
    out[0, target_class].backward()
    
    handle_f.remove()
    handle_b.remove()
    
    if len(features) == 0 or len(gradients) == 0:
        return None
        
    # Swin output might be (B, L, C) or (B, H, W, C)
    feat = features[0][0].detach().cpu().numpy()
    grad = gradients[0][0].detach().cpu().numpy()
    
    # If it is (L, C), reshape to square
    if len(feat.shape) == 2:
        side = int(np.sqrt(feat.shape[0]))
        feat = feat.reshape(side, side, -1)
        grad = grad.reshape(side, side, -1)
    
    weights = np.mean(grad, axis=(0, 1))
    
    cam = np.zeros(feat.shape[0:2], dtype=np.float32)
    for i, w in enumerate(weights):
        cam += w * feat[:, :, i]
        
    cam = np.maximum(cam, 0)
    
    if np.max(cam) == 0:
        cam_normalized = cam
    else:
        cam_normalized = cam / np.max(cam)
        
    # --------------------------------------------------
    # Dynamic Thresholding: Use a lower threshold if 
    # activations are weak, and ensure a minimum spread.
    # --------------------------------------------------
    
    # Apply a lower base threshold for visibility
    base_threshold = 0.3
    cam_normalized[cam_normalized < base_threshold] = 0
    
    # Re-normalize to [0, 1] if there's any signal left
    cam_max = np.max(cam_normalized)
    if cam_max > 0:
        cam_normalized = cam_normalized / cam_max

    # Blur for smoothness
    cam_normalized = cv2.GaussianBlur(cam_normalized, (5, 5), 0)

    # Sharpen hotspots using a power transform
    cam_normalized = np.power(cam_normalized, 1.5)
        
    cam_resized = cv2.resize(cam_normalized, original_image.size)
    
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    heatmap = np.float32(heatmap) / 255
    
    orig_np = np.array(original_image).astype(np.float32) / 255
    if len(orig_np.shape) == 2:
        orig_np = cv2.cvtColor(orig_np, cv2.COLOR_GRAY2RGB)
    
    orig_bgr = orig_np[:, :, ::-1]
    
    # Blend: Only apply heatmap where cam_resized > 0
    # This keeps the rest of the image clean
    alpha_map = cam_resized[:, :, np.newaxis] * 0.7 # Max opacity 0.7
    cam_img = heatmap * alpha_map + orig_bgr * (1 - alpha_map)
    
    if np.max(cam_img) > 0:
        cam_img = cam_img / np.max(cam_img)
        
    cam_img = np.uint8(255 * cam_img[:, :, ::-1])
    
    success, buffer = cv2.imencode('.jpg', cam_img)
    if not success:
        return None
        
    heatmap_base64 = base64.b64encode(buffer).decode('utf-8')
    return heatmap_base64


def predict_image(model, image_file, generate_heatmap=False):

    device = torch.device("cpu")

    original_image = Image.open(image_file).convert("RGB")
    image = resize(original_image)
    image_tensor = to_tensor(image)
    image_tensor = normalize(image_tensor)

    image_tensor = image_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.sigmoid(outputs).cpu().numpy()[0]

    # --------------------------------------
    # Convert probabilities to dictionary
    # --------------------------------------

    predictions = {
        LABELS[i]: float(probs[i])
        for i in range(len(LABELS))
    }

    # --------------------------------------
    # Determine disease labels
    # --------------------------------------

    threshold = 0.5

    disease_labels = [
        LABELS[i]
        for i in range(len(LABELS))
        if probs[i] >= threshold and LABELS[i] != "No Finding"
    ]

    # --------------------------------------
    # Patient readable result
    # --------------------------------------

    if len(disease_labels) > 0:
        patient_result = "Lung Disease Detected"
    else:
        patient_result = "Normal"

    # --------------------------------------
    # Fusion probability
    # (max disease probability except No Finding)
    # --------------------------------------

    disease_probs = [
        probs[i]
        for i in range(len(LABELS))
        if LABELS[i] != "No Finding"
    ]

    disease_probability = float(max(disease_probs))

    # --------------------------------------
    # Heatmap Generation
    # --------------------------------------

    heatmap_base64 = None
    if generate_heatmap:
        # Find the class with the highest probability
        target_class = int(np.argmax(probs))
        
        # If the highest probability is "No Finding", target the highest disease instead
        if LABELS[target_class] == "No Finding" and len(disease_probs) > 0:
            target_class = int(np.argmax([probs[i] if LABELS[i] != "No Finding" else -1 for i in range(len(LABELS))]))

        with torch.enable_grad():
            image_tensor.requires_grad_(True)
            heatmap_base64 = generate_gradcam_heatmap(model, image_tensor, original_image, target_class)

    # --------------------------------------
    # Return structure
    # --------------------------------------

    result = {
        "probabilities": predictions,
        "patient_result": patient_result,
        "fusion_probability": disease_probability,
        "detected_diseases": disease_labels
    }
    
    if heatmap_base64:
        result["heatmap_base64"] = heatmap_base64

    return result
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg') # Safe head-less rendering for web servers
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize

class ModelEvaluator:
    """Computes ML validation metrics and exports visual charts as base64 images."""
    def __init__(self):
        pass

    def _fig_to_base64(self, fig):
        """Converts Matplotlib figure into a base64 encoded HTML inline string."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{encoded}"

    def plot_confusion_matrix(self, y_true, y_pred, labels):
        """Renders Confusion Matrix heatmap."""
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=(6, 5))
        # Use simple color palettes suitable for dark / light modes
        im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        ax.figure.colorbar(im, ax=ax)
        
        ax.set(
            xticks=np.arange(cm.shape[1]),
            yticks=np.arange(cm.shape[0]),
            xticklabels=labels, 
            yticklabels=labels,
            title='Confusion Matrix',
            ylabel='True Label',
            xlabel='Predicted Label'
        )
        
        # Rotate text labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Write values in cells
        fmt = 'd'
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(
                    j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black"
                )
                
        fig.tight_layout()
        return self._fig_to_base64(fig)

    def plot_feature_importance(self, importances, feature_names):
        """Renders feature weight bar chart."""
        indices = np.argsort(importances)
        
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.barh(range(len(indices)), np.array(importances)[indices], color='#4f46e5', align='center')
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.set_title('Feature Importance')
        ax.set_xlabel('Relative Importance Value')
        
        fig.tight_layout()
        return self._fig_to_base64(fig)

    def plot_roc_curve(self, model, X_test, y_test, labels):
        """Renders multi-class ROC curve chart."""
        # Check if model has predict_proba
        if not hasattr(model, "predict_proba"):
            return None
            
        y_score = model.predict_proba(X_test)
        n_classes = len(labels)
        
        # Binarize labels for multi-class ROC
        y_test_bin = label_binarize(y_test, classes=list(range(n_classes)))
        
        fig, ax = plt.subplots(figsize=(6, 5))
        
        for i in range(n_classes):
            # If binary class configuration handles
            if n_classes == 2:
                fpr, tpr, _ = roc_curve(y_test, y_score[:, 1])
                roc_auc = auc(fpr, tpr)
                ax.plot(fpr, tpr, label=f"ROC curve (area = {roc_auc:.2f})")
                break
            else:
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
                roc_auc = auc(fpr, tpr)
                ax.plot(fpr, tpr, label=f"{labels[i]} (AUC = {roc_auc:.2f})")
                
        ax.plot([0, 1], [0, 1], 'k--', lw=1.5)
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('Receiver Operating Characteristic (ROC)')
        ax.legend(loc="lower right")
        
        fig.tight_layout()
        return self._fig_to_base64(fig)

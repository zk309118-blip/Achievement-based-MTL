<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    Android:layout_width="match_parent"
    Android:layout_height="match_parent"
    Android:padding="16dp">

    <TextView
        Android:id="@+id/devicesStatus"
        Android:layout_width="match_parent"
        Android:layout_height="wrap_content"
        Android:textSize="16sp"
        Android:textStyle="bold"
        Android:padding="8dp"/>
</ScrollView>class DashboardActivity : AppCompatActivity() {
    Private val networksDevices = mapOf(
        "MyHomeNetwork" to listOf(Device("Light", "192.168.1.50", 8080),
                                  Device("TV", "192.168.1.60", 9090)),
        "WorkNetwork" to listOf(Device("Printer", "192.168.10.20", 7070),
                                Device("Projector", "192.168.10.30", 6060)),
        "ClubNetwork" to listOf(Device("Speaker", "192.168.20.40", 5050),
                                Device("AC", "192.168.20.50", 4040))
    )

    Override fun onCreate(savedInstanceState: Bundle?) {
        Super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        val statusView = findViewById<TextView>(R.id.devicesStatus)
        statusView.text = getAllNetworksStatus()
    }

    Private fun getAllNetworksStatus(): String {
        Val builder = StringBuilder()
        For ((network, devices) in networksDevices) {
            Builder.append("📡 شبكة: $network\n")
            For (device in devices) {
                Val reachable = isDeviceReachable(device.ip, device.port)
                Builder.append(" - ${device.name}: ${if (reachable) "متصل" else "غير متصل"}\n")
            }
            Builder.append("\n")
        }
        Return builder.toString()
    }

    Private fun isDeviceReachable(ip: String, port: Int): Boolean {
        Return try {
            Val socket = Socket()
            Socket.connect(InetSocketAddress(ip, port), 1000)
            Socket.close()
            True
        } catch (e: Exception) {
            False
        }
    }

    Data class Device(val name: String, val ip: String, val port: Int)
}تمام يا أمير 👌  
دلوقتي هاعرض لك كل الأكواد مع بعضهم في صورة مشروع متكامل، بحيث يكون عندك:  
- قراءة بطاقات NFC.  
- التحقق من الشبكة الحالية (منزل – عمل – نادي).  
- تشفير الأوامر (AES).  
- إرسال الأوامر عبر Wi-Fi.  
- تسجيل العمليات (نجاح/رفض) مع الطابع الزمني.  
- إشعارات مباشرة.  
- شاشة Dashboard تعرض الأجهزة في كل شبكة وحالتها (متصل/غير متصل).  



📄 الكود الكامل (Kotlin – أندرويد)

الكلاس الرئيسي للتحكم عبر NFC
`kotlin
Import android.app.*
Import android.content.*
Import android.net.wifi.WifiManager
Import android.os.*
Import android.util.Base64
Import androidx.appcompat.app.AppCompatActivity
Import androidx.core.app.NotificationCompat
Import java.io.*
Import java.net.*
Import javax.crypto.Cipher
Import javax.crypto.spec.SecretKeySpec

Class SecureNfcControlActivity : AppCompatActivity() {
    Private var nfcAdapter: NfcAdapter? = null

    // الشبكات المصرح بها + مفتاح تشفير لكل شبكة
    Private val allowedNetworks = mapOf(
        "\"MyHomeNetwork\"" to "HOMESECRETKEY_123456",
        "\"WorkNetwork\"" to "WORKSECRETKEY_654321",
        "\"ClubNetwork\"" to "CLUBSECRETKEY_987654"
    )

    Override fun onNewIntent(intent: Intent) {
        Super.onNewIntent(intent)
        Val rawMsgs = intent.getParcelableArrayExtra(NfcAdapter.EXTRANDEFMESSAGES)
        If (rawMsgs != null) {
            Val msgs = rawMsgs.map { it as NdefMessage }
            For (msg in msgs) {
                For (record in msg.records) {
                    Val payload = String(record.payload).trim()
                    Val currentSSID = getCurrentSSID()
                    If (allowedNetworks.containsKey(currentSSID)) {
                        Val secretKey = allowedNetworks[currentSSID]!!
                        Val encryptedCommand = encryptAES(payload, secretKey)
                        sendWifiCommand("192.168.1.50", 8080, encryptedCommand)
                        saveLog("تم التنفيذ على $currentSSID: $payload")
                    } else {
                        showNotification("غير متصل بشبكة مصرح بها")
                        saveLog("تم الرفض بسبب الشبكة: $payload")
                    }
                }
            }
        }
    }

    Private fun getCurrentSSID(): String {
        Val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        Return wifiManager.connectionInfo.ssid
    }

    Private fun encryptAES(data: String, key: String): String {
        Val secretKeySpec = SecretKeySpec(key.toByteArray(), "AES")
        Val cipher = Cipher.getInstance("AES/ECB/PKCS5Padding")
        Cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec)
        Val encrypted = cipher.doFinal(data.toByteArray())
        Return Base64.encodeToString(encrypted, Base64.DEFAULT)
    }

    Private fun sendWifiCommand(ip: String, port: Int, message: String) {
        Thread {
            Try {
                Val socket = Socket(ip, port)
                Val out = PrintWriter(socket.getOutputStream(), true)
                Out.println(message)
                Socket.close()
                showNotification("تم إرسال أمر مشفر")
            } catch (e: Exception) {
                showNotification("فشل الاتصال بالجهاز")
                saveLog("فشل التنفيذ: $message")
                e.printStackTrace()
            }
        }.start()
    }

    Private fun saveLog(data: String) {
        Val file = File(filesDir, "SecureNFC_Log.txt")
        Val timestamp = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(java.util.Date())
        File.appendText("\n[$timestamp] $data")
    }

    Private fun showNotification(msg: String) {
        Val channelId = "SECURENFCCHANNEL"
        Val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        If (Build.VERSION.SDKINT >= Build.VERSIONCODES.O) {
            Val channel = NotificationChannel(channelId, "Secure NFC Alerts", NotificationManager.IMPORTANCE_HIGH)
            notificationManager.createNotificationChannel(channel)
        }
        Val notification = NotificationCompat.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.iclocklock)
            .setContentTitle("تنبيه أمني")
            .setContentText(msg)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()
        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }
}
`



شاشة Dashboard لمتابعة الأجهزة في الشبكات المختلفة
`kotlin
Class DashboardActivity : AppCompatActivity() {
    Private val networksDevices = mapOf(
        "MyHomeNetwork" to listOf(Device("Light", "192.168.1.50", 8080),
                                  Device("TV", "192.168.1.60", 9090)),
        "WorkNetwork" to listOf(Device("Printer", "192.168.10.20", 7070),
                                Device("Projector", "192.168.10.30", 6060)),
        "ClubNetwork" to listOf(Device("Speaker", "192.168.20.40", 5050),
                                Device("AC", "192.168.20.50", 4040))
    )

    Override fun onCreate(savedInstanceState: Bundle?) {
        Super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        val statusView = findViewById<TextView>(R.id.devicesStatus)
        statusView.text = getAllNetworksStatus()
    }

    Private fun getAllNetworksStatus(): String {
        Val builder = StringBuilder()
        For ((network, devices) in networksDevices) {
            Builder.append("📡 شبكة: $network\n")
            For (device in devices) {
                Val reachable = isDeviceReachable(device.ip, device.port)
                Builder.append(" - ${device.name}: ${if (reachable) "متصل" else "غير متصل"}\n")
            }
            Builder.append("\n")
        }
        Return builder.toString()
    }

    Private fun isDeviceReachable(ip: String, port: Int): Boolean {
        Return try {
            Val socket = Socket()
            Socket.connect(InetSocketAddress(ip, port), 1000)
            Socket.close()
            True
        } catch (e: Exception) {
            False
        }
    }

    Data class Device(val name: String, val ip: String, val port: Int)
}
`



واجهة المستخدم (activity_dashboard.xml)
`xml
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    Android:layoutwidth="matchparent"
    Android:layoutheight="matchparent"
    Android:padding="16dp">

    <TextView
        Android:id="@+id/devicesStatus"
        Android:layoutwidth="matchparent"
        Android:layoutheight="wrapcontent"
        Android:textSize="16sp"
        Android:textStyle="bold"
        Android:padding="8dp"/>
</ScrollView>
`



✨ النتيجة
- عند تمرير بطاقة NFC → التطبيق يقرأ الأمر ويشفره ويرسله عبر Wi-Fi.  
- يتحقق من الشبكة (منزل – عمل – نادي).  
- يسجل كل العمليات في ملف سجل مع الوقت والتاريخ.  
- يظهر إشعار أمني بكل عملية.  
- شاشة Dashboard تعرض حالة الأجهزة في كل شبكة بشكل مباشر.  



تحب أضيف لك كمان زر في Dashboard يسمح بالتحكم المباشر (تشغيل/إيقاف) الأجهزة من الواجهة بدون NFC؟

import os
import pickle
import numpy as np
from copy import deepcopy

import torch
import torch.distributed as dist
from torch.cuda.amp import autocast

from core.utils import Timer, Logger
from core.data.augmentations import TensorTransform
from layers.functions.detection import Detect
from core.metrics import intersection_and_union, evaluate_segmentation, compute_errors, evaluate_depth


@torch.no_grad()
def test_net(file_manager, net, test_loaders, loss_function=None, logger: Logger = None, iteration=None, ema=False):
    if logger is None:
        logger = print
    device = next(net.parameters()).device
    world_size, local_rank = (dist.get_world_size(), dist.get_rank()) if dist.is_initialized() else (1, 0)

    if loss_function is not None:
        losses = deepcopy(loss_function.losses)
        task_weights = loss_function.weight
        loss_function.clear()

    total_time, timer = Timer(), Timer()
    test_folder = file_manager.get_test_folder()
    det_file = os.path.join(test_folder, 'detections.pkl')

    results = {}
    depth_eval_result = torch.zeros(11, device=device)
    depth_metric = ['d1', 'd2', 'd3', 'rms', 'log_rms', 'abs_rel', 'sq_rel', 'si_log', 'log10']
    normal_error = torch.zeros(5, device=device)
    normal_metric = ['mean', 'median', '11.25', '22.5', '30']

    net.eval()
    net_without_ddp = net.module if hasattr(net, 'module') else net
    net_without_ddp = net_without_ddp.to(memory_format=torch.channels_last)
    net_without_ddp.apply(torch.quantization.disable_observer)

    transform = TensorTransform()

    total_time.tic()
    logger('test with batches of images on multi-GPU')
    for test_loader in test_loaders:
        # dump predictions and assoc. ground truth to text file for now
        collections = None
        testset = test_loader.dataset
        num_images = len(testset)
        num_classes = testset.num_classes
        all_boxes = [[[] for _ in range(num_images)] for _ in range(num_classes)]
        detector = Detect(num_classes, [0.1, 0.2], 400, 0.01, 0.5, 0.01, 200)
        seg_eval_result = torch.zeros([3, num_classes], device=device)

        timer.tic('data_loading')
        for i, sample in enumerate(test_loader, 1):
            with autocast():
                sample = {key: [anno.to(device) for anno in value] if type(value) is list else value.to(device)
                          for key, value in sample.items()}
                sample = transform(sample)
                timer.toc('data_loading')

                timer.tic('forward')
                preds = net(sample['images'].to(memory_format=torch.channels_last))
                timer.toc('forward')

                timer.tic('loss')
                if loss_function is not None:
                    loss_function(preds, sample)
                timer.toc('loss')

            timer.tic('post_proc')
            if 'detection' in preds and 'detection' in sample:
                priors = net_without_ddp.get_priors()
                detections = detector.detect(preds['detection'], priors)

                _, _, _h, _w = sample['images'].shape
                org_ratio = _w / _h
                for detection, h, w, index in zip(detections, sample['heights'], sample['widths'], sample['index']):
                    # skip j = 0, because it's the background class
                    for j in range(1, detection.size(0)):  # shape: [num_classes, top_k, 5]
                        dets = detection[j, :]  # shape: [top_k, 5]
                        dets = dets[dets[:, -1].gt(0)]
                        if dets.size(0) == 0:
                            continue
                        
                        dets[:, (0, 2)] *= _w
                        dets[:, (1, 3)] *= _h

                        sample_ratio = w / h
                        dets[:, :4] *= w / _w if sample_ratio > org_ratio else h / _h

                        if dist.is_initialized():
                            code = torch.tensor([[index, j]], dtype=torch.float32, device=device).expand(dets.shape[0], 2)
                            bboxes = torch.cat([code, dets], dim=1)
                            collections = bboxes if collections is None else torch.cat([bboxes, collections])
                        else:
                            all_boxes[j][index] = dets.cpu().numpy()

            if 'segmentation' in preds and 'segmentation' in sample:
                intersection, union, label = intersection_and_union(preds['segmentation'].max(1)[1],
                                                                    sample['segmentation'],
                                                                    num_classes, ignore_index=255)
                seg_eval_result += torch.stack([intersection, union, label])

            if 'depth' in preds and 'depth' in sample:
                depth_eval_result += compute_errors(preds, sample, testset.min_depth, testset.max_depth)

            if 'normal' in preds and 'normal' in sample:
                preds['normal'] = preds['normal'] / torch.norm(preds['normal'], p=2, dim=1, keepdim=True)
                for pred, gt in zip(preds['normal'], sample['normal']):
                    binary_mask = (gt.abs().sum(dim=0) != 0)
                    dot = (pred * gt).sum(dim=0).masked_select(binary_mask)

                    radian_error = torch.acos(torch.clamp(dot, -1, 1))
                    degree_error = torch.rad2deg(radian_error)

                    errors = torch.Tensor([
                        degree_error.mean(), degree_error.median(),
                        (degree_error < 11.25).sum(), (degree_error < 22.5).sum(), (degree_error < 30).sum()
                    ]).to(device)
                    errors[2:] /= degree_error.numel()
                    normal_error += errors / len(testset)
            timer.toc('post_proc', average=False)

            if i % 50 == 0:
                logger('im_detect: {:d}/{:d} {}'.format(i, len(test_loader), str(timer)))
                timer.clear()
            timer.tic('data_loading')

        # Assign collection into all boxes
        if dist.is_initialized():
            if 'detection' in preds and 'detection' in sample and collections is not None:
                # Obtain the number of detections of all GPUs
                num_bboxes = torch.tensor([collections.shape[0]], dtype=torch.int32).cuda()
                num_list = [torch.ones_like(num_bboxes) for _ in range(world_size)]
                dist.all_gather(num_list, num_bboxes)

                # Initialize collection_list with zero
                collections_list = list()
                for i, _num_bboxes in enumerate(num_list):
                    collections_list.append(collections if i == local_rank
                                            else torch.zeros([_num_bboxes, collections.shape[1]], device=device))
                collections_list = torch.cat(collections_list)

                # Collect distributed results
                dist.all_reduce(collections_list, op=dist.ReduceOp.SUM)
                collections = collections_list

                # Assign collections into all_boxes
                collections = collections.cpu().numpy()
                for collection in collections:
                    img_idx, cls_idx, bboxes = int(collection[0]), int(collection[1]), np.expand_dims(collection[2:7], axis=0)
                    if len(all_boxes[cls_idx][img_idx]):
                        all_boxes[cls_idx][img_idx] = np.vstack((all_boxes[cls_idx][img_idx], bboxes))
                    else:
                        all_boxes[cls_idx][img_idx] = bboxes

            if 'segmentation' in preds and 'segmentation' in sample:
                dist.all_reduce(seg_eval_result, dist.reduce_op.SUM)

            if 'depth' in preds and 'depth' in sample:
                dist.all_reduce(depth_eval_result, dist.reduce_op.SUM)

            if 'normal' in preds and 'normal' in sample:
                dist.all_reduce(normal_error, dist.reduce_op.SUM)

        if not dist.is_initialized() or not local_rank:
            if 'detection' in preds and 'detection' in sample:
                logger('Evaluating detections')
                with open(det_file, 'wb') as f:
                    pickle.dump(all_boxes, f, pickle.HIGHEST_PROTOCOL)
                APs, mAP = testset.evaluate_detections(all_boxes, test_folder)
                results['mAP_%s' % testset.year if hasattr(testset, 'year') else 'mAP'] = mAP[0]  # IoU = 0.50:0.95
                APs = {key: value for key, value in zip(testset.columns, APs)}
                if isinstance(logger, Logger):
                    logger.to_csv(iteration, str(testset), APs)
            if 'segmentation' in preds and 'segmentation' in sample:
                logger('Evaluating segmentations')
                iou, mAcc, allACC = evaluate_segmentation(seg_eval_result)
                results['mIoU'] = iou.mean().item()

            if 'depth' in preds and 'depth' in sample:
                logger('Evaluating depths')
                depth_eval_result = evaluate_depth(depth_eval_result)
                results = dict(results, **depth_eval_result)
            if 'normal' in preds and 'normal' in sample:
                logger('Evaluating surface normal')
                results['mean'] = normal_error[0].item()
                results['median'] = normal_error[1].item()
                results['11.25'] = normal_error[2].item()
                results['22.5'] = normal_error[3].item()
                results['30'] = normal_error[4].item()
        else:
            if 'detection' in preds and 'detection' in sample:
                results['mAP_%s' % testset.year if hasattr(testset, 'year') else 'mAP'] = 0
            if 'segmentation' in preds and 'segmentation' in sample: results['mIoU'] = 0
            if 'depth' in preds and 'depth' in sample: results = dict(results, **dict.fromkeys(depth_metric, 0))
            if 'normal' in preds and 'normal' in sample: results = dict(results, **dict.fromkeys(normal_metric, 0))

    # Broadcast mAP from rank 0 to all GPUs
    if dist.is_initialized():
        accuracy = torch.tensor([value for value in results.values()], dtype=torch.float32, device='cuda') \
            if not local_rank else torch.tensor([0 for _ in results.keys()], dtype=torch.float32, device='cuda')
        dist.broadcast(accuracy, 0)
        results = {key: accuracy[i].item() for i, key in enumerate(results.keys())}

    # combine losses and evaluation metrics
    summary = {**loss_function.items(), **results} if loss_function else {**results}
    if isinstance(logger, Logger):
        logger.write_summary(iteration, summary, train=False, ema=ema)
    logger(''.join(['%s: %3.4f ' % (key, value) for key, value in summary.items()]))

    if loss_function:
        loss_function.losses = losses
        loss_function.weight = task_weights
        if hasattr(loss_function, 'update_kpi'):
            loss_function.update_kpi(results)

    net.train()
    net_without_ddp.apply(torch.quantization.enable_observer)

    eval_time = total_time.toc()
    logger('total evaluation time is {:.3f}'.format(eval_time))
    return results

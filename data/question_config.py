"""
data/question_config.py — Cấu hình từ khóa cho câu hỏi Khoa học Gemini API.
"""

# Cấu hình từ khóa theo chủ đề gốc và phân cấp độ khó. Tối thiểu 10 từ khóa mỗi độ khó/chủ đề
TOPIC_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "tư duy IQ & đố vui": {
        "easy": [
            "câu đố mẹo dân gian vui", "câu đố chữ nghĩa về hình khối", 
            "câu hỏi đố vui con vật", "câu đố đố chữ về đồ vật",
            "đoán tên đồ vật qua công dụng", "câu đố chữ cái tiếng mẹ đẻ",
            "câu đố dân gian bằng thơ", "câu hỏi logic đếm số lượng chân",
            "đoán con vật qua tiếng kêu miêu tả", "câu đố thời gian buổi sáng tối",
            "câu đố mẹo về phương hướng", "logic chia kẹo đơn giản",
            "câu đố về các ngày trong tuần", "đố chữ về tên các loài cây",
            "câu hỏi suy luận tình huống gia đình", "đố mẹo về hiện tượng thời tiết",
            "câu đố đếm số lượng ngón tay ngón chân", "logic đi chợ mua đồ cơ bản",
            "câu đố về các phương tiện giao thông", "đố vui về nghề nghiệp qua mô tả"
        ],
        "medium": [
            "quy luật dãy số đơn giản", "câu hỏi tư duy nhanh",
            "suy luận logic đời sống", "logic cân thăng bằng qua câu chữ",
            "câu đố mẹo về ngôn ngữ", "quy luật dãy chữ cái",
            "giải mã anagram từ đơn giản", "suy luận logic ai là kẻ nói dối",
            "bài toán tính góc kim đồng hồ", "logic lịch ngày tháng",
            "bài toán đong nước bằng bình", "suy luận vị trí ngồi qua mô tả",
            "quy luật dãy số Fibonaci cơ bản", "câu đố diêm logic thuần chữ",
            "bài toán sang sông kinh điển", "suy luận quan hệ họ hàng phức tạp",
            "logic chia tiền thừa", "câu hỏi mẹo về tốc độ làm việc",
            "phân tích tình huống có điều kiện", "bài toán mật khẩu số đơn giản"
        ],
        "hard": [
            "suy luận logic mệnh đề", "mật mã học mã hóa thay thế", 
            "phá án logic suy luận từ lời khai", "câu đố mẹo đánh lừa tư duy",
            "bài toán tháp Hà Nội qua mô tả", "câu đố logic phân tích tổ hợp",
            "suy luận chuỗi nhân quả", "bài toán logic băng chuyền",
            "tưởng tượng không gian qua mô tả chữ", "logic quy luật chuỗi ký tự phức tạp",
            "bài toán lấp đầy khối lượng", "suy luận logic đa điều kiện",
            "mật mã Vigenère cơ bản", "phân tích nghịch lý thời gian đơn giản",
            "bài toán tối ưu hóa đường đi ngắn nhất", "suy luận logic Sudoku qua luật text",
            "câu hỏi trinh thám suy luận động cơ", "bài toán chia gia tài phức tạp",
            "logic trò chơi bốc sỏi", "bài toán xác suất bốc thăm có hoàn lại"
        ],
        "nightmare": [
            "bài toán ma trận logic chữ", "nghịch lý logic", "bài toán Einstein", 
            "câu hỏi tư duy triết học logic", "logic topo học qua mô tả",
            "giải mật thư thuật toán mã hóa", "bài toán Monty Hall",
            "nghịch lý kẻ nói dối", "lý thuyết trò chơi (game theory)",
            "toán tử logic boolean", "nghịch lý Zeno qua mô tả toán học",
            "bài toán người du lịch (TSP) dạng text", "logic mờ (fuzzy logic) ứng dụng",
            "hệ chuyên gia suy luận tiến lùi", "bài toán đồng thuận phân tán",
            "nghịch lý con quạ của Hempel", "suy luận Bayes trong tình huống mập mờ",
            "logic lượng tử trừu tượng", "bài toán bữa tối của các triết gia",
            "giải thuật đệ quy quay lui bằng mô tả"
        ]
    },
    "toán học": {
        "easy": [
            "bài toán đố vui đếm đồ vật", "so sánh số lượng lớn bé",
            "phép cộng trừ cơ bản bằng lời", "nhận biết chẵn lẻ qua tình huống",
            "so sánh cao thấp dài ngắn", "nhận dạng giá trị hàng chục đơn vị",
            "đọc số đếm ngẫu nhiên", "tìm số liền trước liền sau",
            "bài toán mua bán bằng tiền lẻ", "bài toán chu vi kẹo bánh đơn giản",
            "tính tổng số tuổi", "chia đều đồ vật cho các bạn",
            "nhận biết ngày tháng trên lịch", "đếm bước chân",
            "phép tính gấp đôi và chia đôi", "tính nhẩm số kẹo còn lại",
            "đo lường độ dài bằng gang tay", "bài toán xếp hàng ngang dọc",
            "tính số lượng bánh xe", "cộng dồn số lượng con vật"
        ],
        "medium": [
            "đố vui bảng cửu chương", "tính nhẩm nhanh qua tình huống",
            "đổi đơn vị đo lường cơ bản", "bài toán tính chu vi thực tế",
            "bài toán chia phần diện tích", "phép tính phân số qua chia bánh",
            "tính trung bình cộng điểm số", "cách tính phần trăm giảm giá",
            "đổi thời gian giờ phút giây", "bài toán đuổi kịp vận tốc",
            "phương trình bậc nhất một ẩn qua lời", "tính tỉ lệ bản đồ",
            "bài toán năng suất làm chung công việc", "tính lãi suất đơn giản",
            "tìm Ước chung lớn nhất qua đố chữ", "phân tích ra thừa số nguyên tố",
            "bài toán chuyển động ngược chiều", "tính thể tích hình hộp chữ nhật",
            "áp dụng định lý Thales qua văn bản", "bài toán vòi nước chảy vào bể"
        ],
        "hard": [
            "xác suất thống kê cơ bản", "phương trình lượng giác", 
            "thuật toán tìm số nguyên tố", "bất đẳng thức Cauchy", 
            "bài toán tối ưu hóa cơ bản", "thể tích và diện tích khối tròn xoay", 
            "phương trình vô tỉ", "hệ phương trình đa thức", 
            "tổ hợp chỉnh hợp xác suất", "cấp số cộng và cấp số nhân",
            "giới hạn của hàm số", "đạo hàm và ý nghĩa vật lý",
            "tích phân tính diện tích phẳng", "hình học không gian tính khoảng cách",
            "khảo sát hàm số bậc ba", "nhị thức Newton",
            "phương trình mặt phẳng trong không gian Oxyz", "số phức cơ bản",
            "bài toán cực trị hình học", "quy nạp toán học"
        ],
        "nightmare": [
            "tích phân bội và giải tích vector", "lý thuyết đồ thị và thuật toán đường đi", 
            "giải tích phức", "cấu trúc đại số trừu tượng",
            "hình học vi phân", "phương trình đạo hàm riêng",
            "phương trình vi phân ngẫu nhiên", "đại số tuyến tính không gian vector",
            "lý thuyết số giải tích", "chuỗi Fourier và biến đổi Laplace",
            "không gian Banach và Hilbert", "lý thuyết Galois",
            "cơ sở của topo đại số", "giải tích hàm",
            "lý thuyết độ đo và tích phân Lebesgue", "đại số Lie",
            "lý thuyết biểu diễn nhóm", "phương pháp phần tử hữu hạn",
            "chuỗi Markov thời gian liên tục", "hình học đại số cơ bản"
        ]
    },
    "thế giới tự nhiên & sinh học": {
        "easy": [
            "hiện tượng thời tiết mưa nắng", "tập tính vật nuôi trong nhà",
            "đố vui tên các loại trái cây", "chức năng bộ phận cơ thể người",
            "đặc điểm các loài chim quen thuộc", "chu kỳ ngày đêm tự nhiên",
            "chuỗi thức ăn cơ bản của thú", "ý nghĩa tiếng kêu động vật",
            "sự khác biệt tĩnh vật sinh vật", "đố vui màu sắc các loại hoa",
            "các loại rau củ ăn hàng ngày", "sự phát triển của hạt thành cây",
            "tập tính ngủ đông của gấu", "nhận biết động vật sống dưới nước",
            "các bộ phận của một cái cây", "ích lợi của cây xanh",
            "động vật đẻ trứng và đẻ con", "sự biến đổi của nòng nọc thành ếch",
            "vai trò của giun đất", "nhận biết các loại gia cầm"
        ],
        "medium": [
            "vòng đời tiến hóa của côn trùng", "hiện tượng quang hợp của cây xanh", 
            "phân loại động vật ăn cỏ và ăn thịt", "chức năng hệ tuần hoàn và hô hấp",
            "cấu trúc động vật có xương sống", "nguyên lý truyền máu cơ bản",
            "cấu tạo tế bào thực vật và động vật", "khái niệm môi trường sinh thái",
            "hệ thống tiêu hóa ở con người", "tập tính sinh sản của loài cá",
            "sự phân bố thảm thực vật", "cơ chế thoát hơi nước ở lá",
            "mối quan hệ cộng sinh", "hệ miễn dịch cơ bản của người",
            "cấu tạo và chức năng của hoa", "chu trình cacbon và nitơ trong tự nhiên",
            "tác động của ô nhiễm môi trường", "cấu tạo mắt người",
            "sự hình thành hóa thạch cơ bản", "phân loại các giới sinh vật"
        ],
        "hard": [
            "di truyền học Mendel", "cơ chế hệ miễn dịch đặc hiệu", 
            "thuyết tiến hóa chọn lọc tự nhiên", "chuyển hóa vật chất trong tế bào",
            "di truyền học quần thể", "đột biến gen và nhiễm sắc thể",
            "bằng chứng tiến hóa qua hóa thạch", "động lực học quần thể sinh vật",
            "cơ chế phiên mã và dịch mã", "sự phân bào nguyên phân giảm phân",
            "hô hấp tế bào và chu trình Krebs", "cấu trúc không gian của ADN",
            "di truyền liên kết giới tính", "cơ chế hoạt động của hormone",
            "sinh thái học quần xã", "chọn giống vật nuôi và cây trồng",
            "công nghệ tế bào thực vật", "sự phát sinh sự sống trên Trái Đất",
            "hóa sinh của quá trình quang hợp", "cân bằng nội môi trong cơ thể"
        ],
        "nightmare": [
            "kỹ thuật di truyền và y học", "công nghệ sinh học CRISPR", 
            "động học enzyme", "cơ chế sinh bệnh học phân tử",
            "mô hình toán học trong sinh thái", "cấu trúc phân tử protein",
            "sinh lý học thực vật nâng cao", "miễn dịch học tế bào",
            "công nghệ biệt hóa tế bào gốc", "sinh học lượng tử ứng dụng",
            "di truyền học biểu sinh (epigenetics)", "sinh học cấu trúc (structural biology)",
            "dược lý học phân tử", "sinh học hệ thống (systems biology)",
            "cơ chế truyền tín hiệu tế bào", "vi sinh vật học công nghiệp",
            "tiến hóa phân tử và cây phát sinh chủng loại", "tin sinh học (bioinformatics) ứng dụng",
            "liệu pháp gen trong điều trị ung thư", "tương tác gen-môi trường phức hợp"
        ]
    },
    "vật lý & khoa học vui": {
        "easy": [
            "hiện tượng nam châm hút sắt", "tác dụng của ánh sáng mặt trời", 
            "giải thích tại sao nước đá nổi", "hiện tượng vật nổi vật chìm",
            "sự truyền nhiệt trong tự nhiên", "giải thích tiếng vang từ vách núi",
            "cơ chế tạo âm thanh nhạc cụ", "hiện tượng phản chiếu qua gương",
            "màu sắc của cầu vồng", "nguyên lý lực đẩy lực kéo",
            "sự bay hơi của nước", "tác dụng của bánh xe",
            "hiện tượng tĩnh điện mùa đông", "bóng tối hình thành như thế nào",
            "tại sao cần mặc áo ấm", "cách hoạt động của nhiệt kế cơ bản",
            "sự rơi tự do của đồ vật", "âm thanh truyền qua sợi dây",
            "ánh sáng và bóng râm", "tại sao lốp xe có gai"
        ],
        "medium": [
            "sự khúc xạ ánh sáng cơ bản", "áp suất chất lỏng và khí quyển",
            "vận tốc truyền âm trong các môi trường", "khối lượng riêng và trọng lượng riêng",
            "sức căng bề mặt của chất lỏng", "nguyên lý đòn bẩy và ròng rọc",
            "sự giãn nở nhiệt của chất rắn", "hiện tượng tĩnh điện và tia sét",
            "định luật Ôm cho đoạn mạch", "định luật Archimedes",
            "công suất và hiệu suất cơ bản", "động năng và thế năng",
            "sự truyền nhiệt qua dẫn nhiệt đối lưu bức xạ", "sự phân tích ánh sáng trắng",
            "cấu tạo và nguyên lý của nam châm điện", "mạch điện nối tiếp và song song",
            "định luật phản xạ ánh sáng", "cấu tạo của mắt về mặt quang học",
            "sự nóng chảy và đông đặc", "lực ma sát trượt và ma sát lăn"
        ],
        "hard": [
            "định luật Faraday về cảm ứng điện từ", "các định luật Newton về chuyển động", 
            "chuyển động ném ngang và ném xiên", "giao thoa ánh sáng qua khe Young",
            "mẫu nguyên tử Bohr", "định luật bảo toàn cơ năng",
            "động lượng và va chạm đàn hồi", "thấu kính mỏng và hệ quang học",
            "lực hướng tâm và chuyển động tròn", "lực từ và lực Lorentz",
            "phương trình trạng thái khí lý tưởng", "thuyết động học phân tử chất khí",
            "định luật Coulomb về tĩnh điện", "từ thông và suất điện động cảm ứng",
            "mạch dao động LC", "sóng cơ học và hiệu ứng Doppler",
            "thuyết lượng tử ánh sáng", "cấu tạo hạt nhân nguyên tử",
            "phóng xạ và chu kỳ bán rã", "năng lượng liên kết hạt nhân"
        ],
        "nightmare": [
            "động học các hạt cơ bản", "vật lý hạt nhân và lò phản ứng", 
            "không thời gian Minkowski", "nhiệt động lực học hố đen",
            "hệ phương trình Maxwell", "nguyên lý bất định Heisenberg",
            "lý thuyết trường lượng tử", "lý thuyết siêu dây",
            "hiệu ứng Doppler tương đối tính", "rối lượng tử và viễn tải lượng tử",
            "cơ học phân tích Lagrange và Hamilton", "nhiệt động lực học phi cân bằng",
            "vật lý chất rắn và lý thuyết vùng năng lượng", "tán xạ Compton",
            "phương trình Schrödinger", "vật lý plasma và phản ứng nhiệt hạch",
            "siêu dẫn nhiệt độ cao", "Mô hình Chuẩn (Standard Model) của vật lý hạt",
            "ngưng tụ Bose-Einstein", "lý thuyết nhiễu loạn lượng tử"
        ]
    },
    "địa lý & thiên văn học": {
        "easy": [
            "sự thay đổi bốn mùa", "hiện tượng luân phiên ngày đêm",
            "chu kỳ của mặt trăng", "cách xác định Đông Tây Nam Bắc",
            "tên gọi các hành tinh hệ mặt trời", "sự khác biệt giữa đại dương và lục địa",
            "đặc điểm sinh tồn ở sa mạc", "vòng tuần hoàn của nước",
            "thích nghi của động vật vùng cực", "nhận biết chòm sao qua truyền thuyết",
            "các loại mây trên bầu trời", "hiện tượng sấm sét",
            "tên các châu lục cơ bản", "vai trò của đất đối với cây trồng",
            "nhận biết đồi núi và đồng bằng", "đặc điểm của gió",
            "nước biển mặn như thế nào", "sự khác biệt giữa suối và sông",
            "hiện tượng sương mù", "ngôi sao Bắc Đẩu"
        ],
        "medium": [
            "phân bổ các lục địa và đại dương", "tọa độ địa lý vĩ độ kinh độ",
            "quỹ đạo các hành tinh trong hệ mặt trời", "vận động tự quay của trái đất",
            "cấu tạo các lớp vỏ trái đất", "nguyên nhân núi lửa phun trào",
            "cơ chế nhật thực và nguyệt thực", "cấu trúc dải ngân hà",
            "sự hình thành các đới khí hậu", "từ trường trái đất",
            "hiện tượng thủy triều và lực hút mặt trăng", "sự xói mòn và phong hóa",
            "đặc điểm khí hậu nhiệt đới gió mùa", "khoáng sản và nhiên liệu hóa thạch",
            "bản đồ địa hình và đường đồng mức", "sự hình thành bão và áp thấp nhiệt đới",
            "dòng hải lưu nóng và lạnh", "cấu trúc hệ mặt trời mở rộng (đai Kuiper)",
            "sao băng và sao chổi", "sự trôi dạt lục địa cơ bản"
        ],
        "hard": [
            "thuyết vụ nổ Big Bang", "cấu trúc của hố đen", 
            "cơ cấu dân số và di cư thế giới", "thuyết kiến tạo mảng thạch quyển",
            "đặc điểm các tầng khí quyển", "hệ thống hoàn lưu đại dương",
            "hoàn lưu khí quyển toàn cầu", "sự vận động của sao chổi và tiểu hành tinh",
            "tốc độ vũ trụ cấp 1 và 2", "lực hấp dẫn và hiện tượng thủy triều",
            "chu kỳ Milankovitch và biến đổi khí hậu", "địa mạo học và sự hình thành địa hình",
            "quang phổ sao và phân loại sao", "sự tiến hóa của vũ trụ sơ khai",
            "hiệu ứng nhà kính và nóng lên toàn cầu", "cơ chế El Niño và La Niña",
            "sự hình thành đất và thổ nhưỡng học", "phép chiếu bản đồ và sai số",
            "khoảng cách thiên văn và năm ánh sáng", "sự mở rộng của vũ trụ (định luật Hubble)"
        ],
        "nightmare": [
            "thuyết đa vũ trụ và màng brane", "bản chất vật chất tối và năng lượng tối", 
            "cơ học thiên thể quỹ đạo", "topo học của không thời gian (wormhole)",
            "ứng dụng tương đối hẹp trong GPS", "thiên văn học vô tuyến",
            "bức xạ phông vi sóng vũ trụ", "giới hạn khối lượng Chandrasekhar",
            "địa vật lý mảng nâng cao", "chu kỳ tiến hóa sao (stellar evolution)",
            "khí tượng học động lực học", "địa hóa học đồng vị",
            "nghiên cứu ngoại hành tinh (exoplanets)", "sóng hấp dẫn và nhiễu xạ",
            "đo đạc trọng lực vệ tinh (GRACE)", "thủy động lực học từ tính trong sao",
            "vật lý nhật quyển", "cấu trúc vĩ mô của vũ trụ (Cosmic Web)",
            "lý thuyết lạm phát vũ trụ", "plasma vật lý không gian"
        ]
    }
}